import re

ABNORMAL = "ABNORMAL"
ABSENT = "absent"
ADDITIONAL = True
AFTERNOON = "afternoon"
ALIVE = "alive"
ANONYMOUS = "anonymous"
ANYTIME = "anytime"
BLACK = "black"
BY_BIRTH = "BY_BIRTH"
CANCELLED = "cancelled"
CLOSED = "closed"
COMPLETE = "COMPLETE"
CONSENTED = "consented"
CONTINUOUS = "continuous"
DEAD = "dead"
DECLINED = "Declined"
DEFAULTER = "defaulter"
DELETE = "DELETE"
DONE = "done"
DONT_KNOW = "dont_know"
DWTA = "DWTA"  # don't want to answer'
ERROR = "ERROR"
EVENING = "evening"
FAILED_ELIGIBILITY = "failed eligibility"
FEEDBACK = "feedback"
FEMALE = "F"
HIDE_FORM = "NOT_REQUIRED"
HIGH = "high"
HIGH_PRIORITY = "high"
IGNORE = "ignore"
INCOMPLETE = "INCOMPLETE"
IND = "IND"
INSERT = "INSERT"
LOST_TO_FOLLOWUP = "LTFU"
LOW_PRIORITY = "low"
MALE = "M"
MALIGNANCY = "malignancy"
MEDIUM_PRIORITY = "medium"
MORNING = "morning"
NAIVE = "NAIVE"
NEG = "NEG"
NEVER = "NEVER"
NEW = "New"
NO = "No"
NO_UNCONFIRMED = "no_unconfirmed"
NONE = "none"
NORMAL = "NORMAL"
NOT_ADDITIONAL = False
NOT_APPLICABLE = "N/A"
NOT_DONE = "not_done"
NOT_EVALUATED = "Not evaluated"
NOT_SURE = "not_sure"
OFF_STUDY = "off study"
OFF_STUDY_VISIT = "off study"
OMANG = "OMANG"
ON_ART = "on_art"
ON_STUDY = "on study"
OPEN = "open"
OPTIONAL = True
OTHER = "OTHER"
PARTIAL = "PARTIAL"
PARTICIPANT = "participant"
PENDING = "PENDING"
POS = "POS"
PRESENT = "present"
PRINT = "PRINT"
PURPOSIVELY_SELECTED = "purposively_selected"
QUERY = "QUERY"
QUESTION_RETIRED = "QUESTION_RETIRED"
RANDOM_SAMPLING = "random_sampling"
REFUSED = "REFUSED"
RESOLVED = "resolved"
RESTARTED = "restarted"
SCREENED = "SCREENED"
SEROCONVERSION = "seroconversion"
SHOW_FORM = "NEW"
STOPPED = "stopped"
SUBJECT = "subject"
TBD = "tbd"  # to be determined
TUBERCULOSIS = "TB"
UNK = "UNK"
UNKNOWN = "unknown"
UPDATE = "UPDATE"
UUID_PATTERN = re.compile(
    "[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
)
VIEW = "VIEW"
WARN = "warn"
WEEKDAYS = "weekdays"
WEEKENDS = "weekends"
YES = "Yes"
