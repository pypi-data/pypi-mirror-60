from jinja2 import Environment, FileSystemLoader, Template
from ask_amy.cli.code_gen.jinja_processing import PreprocessingLoader
import json
import os


class CodeGenerator(object):
    def __init__(self, skill_name, aws_skill_role, interaction_model_json):
        _templates_dir = "{}/templates/".format(os.path.dirname(__file__))

        self._config_model = ConfigModel(skill_name, aws_skill_role)
        self._interaction_model = InteractionModel(interaction_model_json)
        self._env = Environment(loader=PreprocessingLoader(_templates_dir), trim_blocks=True, lstrip_blocks=True)

    def create_cli_config(self):
        cli_config_tmpl = self._env.get_template("cli_config.tmpl")
        cli_config_json = cli_config_tmpl.render(config_model=self._config_model)
        self._write_file('cli_config.json', cli_config_json)

    def create_dialog_model(self):
        dialog_model_tmpl = self._env.get_template("dialog_model_master.tmpl")
        dialog_model_json = dialog_model_tmpl.render(interaction_model=self._interaction_model,
                                                     config_model=self._config_model)
        self._write_file('amy_dialog_model.json', dialog_model_json)


    def create_skill_py(self):
        skill_code_tmpl = self._env.get_template("skill_code_master.tmpl")
        skill_code_py = skill_code_tmpl.render(interaction_model=self._interaction_model,
                                                 config_model=self._config_model)
        file_nm = "{}.py".format(self._config_model.skill_name)
        self._write_file(file_nm, skill_code_py)


    def _write_file(self,file_nm,data):
        if os.path.isfile(file_nm) :
            raise FileExistsError("Attempting to OVERWRITE {}".format(file_nm))

        with open(file_nm, 'w') as f:
            f.write(data)


class InteractionModel:
    def __init__(self, interaction_model_json):
        with open(interaction_model_json) as json_file:
            self._interaction_model = json.load(json_file)

        self._slots = self._process_slots()
        self._intents = self._process_intents()

    @property
    def slots(self):
        return self._slots

    @property
    def intents(self):
        return self._intents

    def slot_indexes(self):
        return list(range(len(self._slots)))

    def has_next_slot_index(self, slot_index):
        return True if slot_index < len(self._slots) - 1 else False

    def _process_intents(self):
        intents = []
        for intent in self._interaction_model['interactionModel']['languageModel']['intents']:
            intent_method = self._process_intent_nm(intent['name'])
            if intent_method:
                intents.append({'name': intent['name'],
                                'method_name': intent_method,
                                'method_text': intent_method.replace("_", " ")})
        return intents

    def _process_slots(self):
        slots_for_intent = []
        language_model = self._interaction_model['interactionModel']['languageModel']
        if 'intents' in language_model:
            for intent_item in language_model['intents']:
                intent_nm = intent_item['name']
                if 'slots' in intent_item:
                    slots = intent_item['slots']
                    for slot in slots:
                        slot_nm = slot['name']
                        # todo Need to fix this multiple types ...
                        if not any(d['slot_name'] == slot_nm for d in slots_for_intent):
                            method_name = self._process_intent_nm(intent_nm)
                            slots_for_intent.append({'slot_name': slot_nm, 'method_name': method_name})
        return slots_for_intent

    def _process_intent_nm(self, intent_name):
        method_nm = None
        if intent_name.startswith('AMAZON.'):
            if intent_name == "AMAZON.HelpIntent" or \
                            intent_name == "AMAZON.CancelIntent" or \
                            intent_name == "AMAZON.StopIntent":
                intent_name = None
            else:
                intent_name = intent_name[7:]
        if intent_name is not None:
            method_nm = self._method_name(intent_name)
        return method_nm

    def _method_name(self, intent_name):
        method_name = intent_name[0].lower()
        for char_in_name in intent_name[1:]:
            if char_in_name.isupper():
                method_name += '_' + char_in_name.lower()
            else:
                method_name += char_in_name
        return method_name


class ConfigModel:
    def __init__(self, skill_name, aws_skill_role):
        self._cli_config_model = {"skill_name": skill_name, "aws_skill_role": aws_skill_role}

    @property
    def aws_skill_role(self):
        return self._cli_config_model["aws_skill_role"]

    @property
    def skill_name(self):
        return self._cli_config_model["skill_name"]

    @property
    def class_name(self):
        skill_name = self._cli_config_model["skill_name"]
        class_name = skill_name.replace("_", " ")
        class_name = class_name.title()
        class_name = class_name.replace(" ", "")
        return class_name


def main():
    code_generator = CodeGenerator("boston_info_skill",
                                   "arn:aws:iam::280056172273:role/alexa_lambda_role",
                                   "./templates/interaction_model.json")
    code_generator.create_cli_config()
    code_generator.create_dialog_model()
    code_generator.create_skill_py()


if __name__ == "__main__":
    main()
