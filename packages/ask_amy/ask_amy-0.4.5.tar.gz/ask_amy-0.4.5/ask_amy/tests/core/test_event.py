from ask_amy.tests.test_ask_amy_base import TestCaseASKAmy
from ask_amy.core.event import Event


class TestEvent(TestCaseASKAmy):
    def setUp(self):
        pass

    def test_event_constr(self):
        event_dict = self.load_json_file('event_w_active_session.json')
        event_obj = Event(event_dict)
        event_obj.slot_data_to_session_attributes()
        #print(event_obj)
