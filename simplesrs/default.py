from datetime import timedelta

DEFAULT = {
    'srs': [
        timedelta(minutes=10),  # 0
        timedelta(hours=1),     # 1
        timedelta(hours=4),     # 2
        timedelta(hours=8),     # 3
        timedelta(days=1),      # 4
        timedelta(days=3),      # 5
        timedelta(weeks=1),     # 6
        timedelta(weeks=2),     # 7
        timedelta(weeks=4),     # 8
        timedelta(weeks=16)     # 9
    ],
    'type_': 'markdown',
    'info': {
        'version': '0.1'
    }
}
