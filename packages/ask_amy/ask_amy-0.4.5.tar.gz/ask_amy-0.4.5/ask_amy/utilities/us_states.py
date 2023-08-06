class USSateNamesUtility(object):
    states = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
              "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia",
              "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
              "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts",
              "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
              "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
              "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
              "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
              "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",  "WA": "Washington",
              "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
              }

    @staticmethod
    def state_nm_for_cd(code):
        ret_val = code
        if code in USSateNamesUtility.states:
            ret_val = USSateNamesUtility.states[code]
        return ret_val


    @staticmethod
    def state_cd_for_nm(name):
        ret_val = None
        for key in USSateNamesUtility.states:
            value = USSateNamesUtility.states[key].lower()
            if name.lower() == value:
                ret_val = value
                break
        return ret_val

if __name__ == "__main__":
    print(USSateNamesUtility.state_nm_for_cd('MA'))
    print(USSateNamesUtility.state_cd_for_nm('Massachusetts'))
