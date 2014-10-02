from .settings import ACCESS_LEVELS as BASE_ACCESS_LEVELS


TIME_ZONES = (
    ('GMT-12', '(GMT-12:00) International Date Line West'),
    ('GMT-11', '(GMT-11:00) Midway Island, Samoa'),
    ('GMT-10', '(GMT-10:00) Hawaii'),
    ('GMT-9', '(GMT-9:00) Alaska'),
    ('GMT-8', '(GMT-8:00) Pacific Standard Time'),
    ('GMT-7', '(GMT-7:00) Mountain Standard Time'),
    ('GMT-6', '(GMT-6:00) Central Standard Time'),
    ('GMT-5', '(GMT-5:00) Eastern Standard Time'),
    ('GMT-4:30', '(GMT-4:30) Caracas'),
    ('GMT-4', '(GMT-4:00) Eastern Caribbean Time'),
    ('GMT-3:30', '(GMT-3:30) Newfoundland'),
    ('GMT-3', '(GMT-3:00) Greenland, Buenos Aires'),
    ('GMT-2', '(GMT-2:00) Mid-Atlantic'),
    ('GMT-1', '(GMT-1:00) Cape Verde Time'),
    ('GMT', '(GMT) Western Europe Time'),
    ('GMT+1', '(GMT+1:00) Central European Time'),
    ('GMT+2', '(GMT+2:00) Eastern European Time'),
    ('GMT+3', '(GMT+3:00) Baghdad, Riyadh, Moscow, St. Petersburg'),
    ('GMT+3:30', '(GMT+3:30) Tehran'),
    ('GMT+4:00', '(GMT+4:00) Abu Dhabi, Muscat, Baku, Tbilisi'),
    ('GMT+4:30', '(GMT+4:30) Kabul'),
    ('GMT+5', '(GMT+5:00) Ekaterinburg, Islamabad, Karachi, Tashkent'),
    ('GMT+5:30', '(GMT+5:30) Bombay, Calcutta, Madras, New Delhi'),
    ('GMT+5:45', '(GMT+5:45) Kathmandu'),
    ('GMT+6:00', '(GMT+6:00) Almaty, Dhaka, Colombo'),
    ('GMT+7:', '(GMT+7:00) Bangkok, Hanoi, Jakarta'),
    ('GMT+8', '(GMT+8:00) Beijing, Perth, Singapore, Hong Kong'),
    ('GMT+9', '(GMT+9:00) Tokyo, Seoul, Osaka, Sapporo, Yakutsk'),
    ('GMT+9:30', '(GMT+9:30) Adelaide, Darwin'),
    ('GMT+10', '(GMT+10:00) Eastern Australia, Guam, Vladivostok'),
    ('GMT+11', '(GMT+11:00) Magadan, Solomon Islands, New Caledonia'),
    ('GMT+12', '(GMT+12:00) Auckland, Wellington, Fiji, Kamchatka'),
)

ACCESS_LEVELS = BASE_ACCESS_LEVELS.copy()
ACCESS_LEVELS['public'] = 0

PLANNED_STATUS = (
    (0, 'pending'),
    (1, 'completed'),
    (-1, 'cancelled')
)
