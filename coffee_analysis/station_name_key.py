FOOTNOTE_PATTERN = "\\(.*?\\)|[¹²³⁴⁵⁶⁷⁸⁹*]|\\s+\\d{1,2}\\s*$"


class StationNameKey:
    def display_name(self, column: str) -> str:
        return f"trim(regexp_replace({column}, '{FOOTNOTE_PATTERN}', '', 'g'))"

    def expression(self, column: str) -> str:
        normalized = f"upper(strip_accents({self.display_name(column)}))"
        words = f"trim(regexp_replace({normalized}, '[^A-Z0-9]+', ' ', 'g'))"
        return f"regexp_replace({words}, '\\bN S\\b', 'NOSSA SENHORA', 'g')"
