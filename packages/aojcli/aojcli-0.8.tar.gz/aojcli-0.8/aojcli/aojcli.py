import os
import sys
import argparse
import datetime
import texttable
from . import libaoj

support_oper = ["submit"]

#TODO : get from API
support_lang = ["C", "C++", "Java", "C++11", "C++14", "C#", "D", "Ruby", "Python", "Ptyhon3", "PHP", "JavaScript", "Scala", "Haskell", "OCaml", "Rust", "Go", "Kotlin"]

def error_exit(message, exit_code = -1):
    output = ""
    for line in message:
        output += line
    
    sys.stderr.write(output + "\n")
    exit(exit_code)

def command_submit(api, args):
    try:
        with open(args.file, "r") as source_file:
            source_code = source_file.read()
        
        ret = api.submit(args.problem_id, args.language, source_code)
        print("[submit success]")
        print("Access token for checking result : %s" % ret["token"])
        
    except IOError as e:
        error_exit(str(e))
    except libaoj.AojApiError as e:
        #print e.get_detail()
        error_exit(e.get_message())
        

def command_status(api, args):
    try:
        ret = api.get_my_submit_record(args.problem_id)
    except libaoj.AojApiError as e:
        #print e.get_detail)
        error_exit(e.get_message())
    
    print("[Status of submission(%s)]" % args.problem_id)
    table = texttable.Texttable(max_width=100)
    table.add_row(["judge id", "status", "lang", "submit date", "judge date"])
    for problem in ret:
        submit_date = datetime.datetime.fromtimestamp(problem["submissionDate"] / 1000)
        judge_date = datetime.datetime.fromtimestamp(problem["judgeDate"] / 1000)
        table.add_row([
            "#%s" % problem["judgeId"],
            api.status_codes[problem["status"]],
            problem["language"],
            submit_date,
            judge_date
        ])
    
    print(table.draw())

def main():
    try:
        user_id = os.environ["AOJCLI_ID"]
        password = os.environ["AOJCLI_PASSWORD"]
        
    except KeyError as e:
        message = [
            "Error.\n\n",
            "Required environment values is not set.\n",
            "Please set following environment values.\n",
            "AOJCLI_ID : Your user id of AOJ\n",
            "AOJCLI_PASSWORD : Your password of AOJ\n",
        ]
        error_exit(message)

    try:
        api = libaoj.Api(user_id, password)
    except libaoj.AojApiError as e:
        error_exit(e.get_message())

    parser = argparse.ArgumentParser(description = "AOJ submission tool on CLI")
    subparsers = parser.add_subparsers()

    parser_submit = subparsers.add_parser("submit", help='see `submit -h`')
    parser_submit.add_argument(
        "problem_id",
        const = None,
        help = 'Problem ID',
    )
    parser_submit.add_argument(
        "language",
        const = None,
        choices = support_lang,
        help = 'Laugage of source code'
    )
    parser_submit.add_argument(
        "file",
        const = None,
        help = 'source code file'
    )
    parser_submit.set_defaults(handler=command_submit)

    parser_status = subparsers.add_parser("status", help="see `status -h`")
    parser_status.add_argument(
        "problem_id",
        const = None,
        help = 'Problem ID'
    )
    parser_status.set_defaults(handler=command_status)

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(api, args)
    else:
        parser.print_help()

