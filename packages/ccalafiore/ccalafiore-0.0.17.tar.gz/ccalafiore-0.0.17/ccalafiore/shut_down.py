import os


def if_time_is_out(year, month, day, hour=0, minute=0, second=0, microsecond=0, action='s'):
    # action='s' for shutdown
    # action='r' for restart

    from datetime import datetime
    
    time_out = datetime(year, month, day, hour=hour, minute=minute, second=second, microsecond=microsecond)
    time_now = datetime.now()
    time_is_out = time_out <= time_now
    if time_is_out:
        os.system("shutdown /{} /t 1".format(action))
        #print(time_is_out)

    return time_is_out


def now(year, month, day, hour=0, minute=0, second=0, microsecond=0, action='s'):
    # action='s' for shutdown
    # action='r' for restart

    os.system("shutdown /{} /t 1".format(action))


if_time_is_out(2010, 11, 2, hour=0, minute=0, second=0, microsecond=0, action='r')
straightaway = 10
