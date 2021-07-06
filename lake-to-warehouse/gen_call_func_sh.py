"""Generate call_functions_batch.sh
    - in : from/to date
    - out: shell script for calling cloud functions
"""

import datetime
import json
import sys


def main():
    args = sys.argv
    oldest_dt = datetime.datetime.strptime(args[1], '%Y-%m-%d')
    latest_dt = datetime.datetime.strptime(args[2], '%Y-%m-%d')
    
    # check
    if oldest_dt >= latest_dt:
        print('oldest_dt must be less than latest_dt.')
        sys.exit(1)
    
    # split day by day
    target_dates = []
    _start = oldest_dt
    _end = _start + datetime.timedelta(days=1)
    while _end <= latest_dt:
        target_dates.append(_start.strftime(format='%Y-%m-%d'))
        _start = _end
        _end = _start + datetime.timedelta(days=1)
    
    # make script string
    base_str = "gcloud pubsub topics publish ingested-slackdata-to-gcs --project=salck-visualization"
    cmd_lines = []
    for i, target_date in enumerate(target_dates):
        # comment
        comment_str = "echo exec trigger function {}".format(i+1)
        cmd_lines.append(comment_str)
        # main execution
        blob_dir = f"slack_lake/daily-ingest_target-date_{target_date}"
        opt = "{\\\"data\\\":{\\\"message\\\":\\\"Manual Publish with gcloud\\\",\\\"blob-dir-path\\\":" + f"\\\"{blob_dir}\\\"" + "}}"
        opt_str = f"--message=\"{opt}\""
        cmd_lines.append(base_str + " " + opt_str)
        # sleep
        sleep_time_sec = 300
        cmd_lines.append(f"echo sleep {sleep_time_sec} seconds until next execution ...")
        cmd_lines.append(f"sleep {sleep_time_sec}")

    # write script
    with open('call_functions_batch.sh', 'w') as f:
        f.write("\n".join(cmd_lines))


if __name__ == "__main__":
    args = sys.argv
    
    # parse args
    if len(args) != 3:
        print('3 args are required.')
        print('{} args are input.'.format(len(args)))
        print('1st positional arg is oldest date (YYYY-MM-DD)')
        print('2nd positional arg is latest date (YYYY-MM-DD)')
        sys.exit(1)
    main()

