#!/usr/bin/env python
from notion.client import NotionClient
import notion
import datetime
import notion
import argparse
import sys
import os
import json
import stat
import subprocess


def is_file(filepath):
    if os.path.exists(filepath):
        filestat = os.stat(filepath)
        return filestat is not None and not stat.S_ISDIR(filestat.st_mode)
    return False


def load_config_file(config_json_path):
    if not is_file(config_json_path):
        sys.exit("config file '%s' not found" % config_json_path)

    with open(config_json_path) as config_file:
        config = json.load(config_file)
        client = NotionClient(token_v2=config["token_v2"])
        return (
            client,
            client.get_collection_view(config["sync_root"]),
            config["task_name"] if "task_name" in config else None,
        )


def update_row_field(row, column_name, value):
    for entry in row.schema:
        if entry["name"] == column_name:
            row.set_property(entry["id"], value)


def any_row_field(row, column_name, value_lambda):
    return any(
        value_lambda(row.get_property(entry["id"]))
        for entry in row.schema
        if entry["name"] == column_name
    )


def append_log_to_row_body(row, start_time, run_args, output):
    header = row.children.add_new(notion.block.HeaderBlock)
    header.title = "Run at %s" % start_time.isoformat()
    header.move_to(row, position="first-child")

    codeblock = row.children.add_new(notion.block.CodeBlock)
    codeblock.title = output
    codeblock.move_to(header, position="after")

    if len(run_args):
        subheader = row.children.add_new(notion.block.TextBlock)
        subheader.title = "`" + " ".join(run_args) + "`"
        subheader.move_to(header, position="after")


def run_task(command_args):
    if len(command_args) < 1:
        return "no command was provided %s" % sys.argv, 1

    try:
        p = subprocess.Popen(" ".join(command_args), stdout=subprocess.PIPE, shell=True)
        chunks = []
        while True:
            chunk = p.stdout.read()
            if len(chunk) == 0:
                break
            chunks.append(chunk.decode("utf-8"))
        p.wait()
    except:
        return (
            "Error running command '%s'\n  %s"
            % (" ".join(command_args), "\n  ".join([str(x) for x in sys.exc_info()])),
            1,
        )

    return "".join(chunks), p.returncode


def create_job_row(collection, name):
    new_row = collection.add_row()
    new_row.set_property("Name", name)
    return new_row


def parse_args():
    parser = argparse.ArgumentParser(
        description="Runs a command and reports the result back to a collection row on Notion"
    )

    parser.add_argument(
        "--config",
        "-c",
        metavar="config",
        type=str,
        default="./config.json",
        help="Path to a config file",
    )

    parser.add_argument(
        "--task_name",
        "-n",
        metavar="task_name",
        type=str,
        help="The task name (overrides config.json)",
    )

    parser.add_argument(
        "--log_failure_only",
        dest="log_failure_only",
        action="store_true",
        default=False,
        help="Append an entry to the log only when the command fails",
    )

    parser.add_argument("command_args", nargs="*")
    return parser.parse_args(sys.argv[1:])


def main():
    args = parse_args()
    client, root_view, job_title = load_config_file(args.config)

    if job_title is None:
        if args.task_name == None:
            sys.exit("No task_name set in CLI argument or config file")
        else:
            job_title = args.task_name

    rows = root_view.collection.get_rows()
    matching_rows = [row for row in rows if row.title == job_title]
    rows_to_update = (
        [create_job_row(root_view.collection, job_title)]
        if len(matching_rows) == 0
        else matching_rows
    )

    start_time = datetime.datetime.now()
    for row in rows_to_update:
        update_row_field(row, "Status", "Running")
        update_row_field(row, "Last Run", notion.collection.NotionDate(start_time))
        update_row_field(row, "Runtime", "")

    output, exitcode = run_task(args.command_args)

    end_time = datetime.datetime.now()
    elapsed = end_time - start_time
    elapsed_time_str = "{0:.2f}s".format(elapsed.total_seconds())

    for row in rows_to_update:
        update_row_field(row, "Status", "Success" if exitcode == 0 else "Failed")
        update_row_field(row, "Runtime", elapsed_time_str)
        if (not args.log_failure_only) or exitcode == 1:
            append_log_to_row_body(row, start_time, args.command_args, output)

    any_failed = any(
        (any_row_field(row, "Status", lambda x: x == "Failed") for row in rows)
    )
    requested_icon = u"❌" if any_failed else u"👍"
    current_icon = root_view.collection.get("icon")
    if current_icon != requested_icon:
        current_icon = root_view.collection.set("icon", requested_icon)


if __name__ == "__main__":
    main()
