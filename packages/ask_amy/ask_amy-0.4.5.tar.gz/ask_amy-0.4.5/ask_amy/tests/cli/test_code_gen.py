from ask_amy.tests.test_ask_amy_base import TestCaseASKAmy
import json
import urllib
import urllib.request
from xml.dom.minidom import parseString

class TestDialog(TestCaseASKAmy):
    def setUp(self):
        pass



    def test_dialog_constr(self):
        iam_attach_role_policy = ['aws', '--output', 'json', 'iam', 'attach-role-policy',
                    '--role-name', 0,
                    '--policy-arn',1,
                    '---next',     2]
        print(self.process_args(iam_attach_role_policy,'one','two'))



    def process_args(self,arg_list,*args):
        # process the arg
        for index in range(0,len(arg_list)):
            if type(arg_list[index]) == int:
                # substitue for args passed in
                if arg_list[index] < len(args):
                    arg_list[index] = args[arg_list[index]]
                # if we more substitutions than args passed delete them
                else:
                    del arg_list[index-1:]
                    break
        return arg_list