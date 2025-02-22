"""
    Create by: apenasrr
    Source: https://github.com/apenasrr/zimatise

    Workflow for automatic processing of aggregated videos, construction of
    timestamps and posting with dynamic summary
    A process aggregator that uses independent solutions

    ZI pind
    MA ss_videojoin
    TI mestamp
    SE nd_files

    Requirements:
    -https://github.com/apenasrr/zipind
    -https://github.com/apenasrr/vidtool
    -https://github.com/apenasrr/tgsender

    ## How to use
    -Place the folder of the 4 required repositories and this repository in the
    same location. Then there must be 5 folders in the same location
    -Enter the 'zimatise' folder and run the zimatise.py file
    -Follow the on-screen instructions
    -For more details, check the documentation for the required repositories

    Do you wish to buy a coffee to say thanks?
    LBC (from LBRY) digital Wallet
    > bFmGgebff4kRfo5pXUTZrhAL3zW2GXwJSX

    We recommend:
    mises.org - Educate yourself about economic and political freedom
    lbry.tv - Store files and videos on blockchain ensuring free speech
    https://www.activism.net/cypherpunk/manifesto.html -  How encryption is essential to Free Speech and Privacy
"""

import logging
import os
import shutil
import time
from pathlib import Path

import vidtool
import zipind
from tgsender import tgsender

import autopost_summary
import moc
import update_description_summary
import utils
from description import single_mode
from header_maker import header_maker
from timestamp_link_maker import timestamp_link_maker, utils_timestamp


def logging_config():

    logfilename = "log-" + "zimatise" + ".txt"
    logging.basicConfig(
        level=logging.INFO,
        format=" %(asctime)s-%(levelname)s-%(message)s",
        handlers=[logging.FileHandler(logfilename, "w", "utf-8")],
    )
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(" %(asctime)s-%(levelname)s-%(message)s")
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)


def menu_ask():

    print("1-Create independent Zip parts for not_video_files")
    print("2-Generate worksheet listing the files")
    print(
        "3-Process reencode of videos marked in column "
        '"video_resolution_to_change"'
    )
    print("4-Group videos with the same codec and resolution")
    print("5-Make Timestamps and Descriptions report")
    print("6-Auto-send to Telegram")

    msg_type_answer = "Type your answer: "
    make_report = int(input(f"\n{msg_type_answer}"))
    if make_report == 1:
        return 1
    elif make_report == 2:
        return 2
    elif make_report == 3:
        return 3
    elif make_report == 4:
        return 4
    elif make_report == 5:
        return 5
    elif make_report == 6:
        return 6
    else:
        msg_invalid_option = "Invalid option"
        raise msg_invalid_option


def play_sound():

    path_file_sound = ""
    os.system(f'start wmplayer "{path_file_sound}"')


def define_mb_per_file(path_file_config, file_size_limit_mb):

    if file_size_limit_mb is not None:
        repeat_size = input(
            f"Define limit of {file_size_limit_mb} " + "MB per file? y/n\n"
        )
        if repeat_size == "n":
            file_size_limit_mb = zipind.zipind.ask_mb_file()
            zipind.zipind.config_update_data(
                path_file_config, "file_size_limit_mb", str(file_size_limit_mb)
            )
    else:
        file_size_limit_mb = zipind.zipind.ask_mb_file()
        zipind.zipind.config_update_data(
            path_file_config, "file_size_limit_mb", str(file_size_limit_mb)
        )
    return file_size_limit_mb


def send_to_moc(send_moc, moc_chat_id, template_moc, folder_path_project):

    if send_moc == 1:
        moc.pipe_publish(moc_chat_id, template_moc, folder_path_project)


def clean_temp_files(autodel_video_temp, folder_path_project):

    list_folder_name_to_delete = [
        "output_videos",
        "videos_encoded",
        "videos_splitted",
    ]
    if autodel_video_temp != 1:
        return

    for folder_name_to_delete in list_folder_name_to_delete:
        path_folder_to_delete = os.path.join(
            folder_path_project, folder_name_to_delete
        )
        if os.path.exists(path_folder_to_delete):
            shutil.rmtree(path_folder_to_delete, ignore_errors=True)
        else:
            pass


def run(
    folder_path_report,
    file_path_report,
    list_video_extensions,
    file_size_limit_mb,
    duration_limit,
    start_index,
    activate_transition,
    hashtag_index,
    dict_summary,
    descriptions_auto_adapt,
    path_summary_top,
    document_hashtag,
    document_title,
    reencode_plan,
    mode,
    send_moc,
    moc_chat_id,
    autodel_video_temp,
):

    folder_path_report = vidtool.get_folder_path(folder_path_report)
    folder_path_project = os.path.dirname(file_path_report)

    folder_path_output = os.path.join(folder_path_project, "output_videos")

    ################################### p1
    utils.ensure_folder_existence([folder_path_output])
    zipind.zipind_core.run(
        path_dir=folder_path_report,
        mb_per_file=file_size_limit_mb,
        path_dir_output=folder_path_output,
        mode=mode,
        ignore_extensions=list_video_extensions,
    )

    ################################### p2
    vidtool.step_create_report_filled(
        folder_path_report,
        file_path_report,
        list_video_extensions,
        reencode_plan,
    )
    ################################### p3
    folder_path_videos_encoded = vidtool.set_path_folder_videos_encoded(
        folder_path_report
    )
    vidtool.ensure_folder_existence([folder_path_videos_encoded])

    # reencode videos mark in column video_resolution_to_change
    vidtool.set_make_reencode(file_path_report, folder_path_videos_encoded)

    ################################### p4
    folder_path_videos_splitted = vidtool.set_path_folder_videos_splitted(
        folder_path_report
    )

    vidtool.ensure_folder_existence([folder_path_videos_splitted])

    folder_path_videos_joined = vidtool.set_path_folder_videos_joined(
        folder_path_report
    )

    vidtool.ensure_folder_existence([folder_path_videos_joined])

    filename_output = vidtool.get_folder_name_normalized(folder_path_report)

    folder_path_videos_cache = vidtool.set_path_folder_videos_cache(
        folder_path_report
    )

    vidtool.ensure_folder_existence([folder_path_videos_cache])

    if reencode_plan == "group":
        # Fill group_column.
        #  Establishes separation criteria for the join videos step
        vidtool.set_group_column(file_path_report)

    # split videos too big
    vidtool.set_split_videos(
        file_path_report,
        file_size_limit_mb,
        folder_path_videos_splitted,
        duration_limit,
    )

    if reencode_plan == "group":
        # join all videos
        vidtool.set_join_videos(
            file_path_report,
            file_size_limit_mb,
            filename_output,
            folder_path_videos_joined,
            folder_path_videos_cache,
            duration_limit,
            start_index,
            activate_transition,
        )

    ################################### p5

    if reencode_plan == "group":

        # make descriptions.xlsx and summary.txt
        timestamp_link_maker(
            folder_path_output=folder_path_project,
            file_path_report_origin=file_path_report,
            hashtag_index=hashtag_index,
            start_index_number=start_index,
            dict_summary=dict_summary,
            descriptions_auto_adapt=descriptions_auto_adapt,
        )

        update_description_summary.main(
            path_summary_top,
            folder_path_project,
            document_hashtag,
            document_title,
        )
    else:
        # create descriptions.xlsx for single reencode
        single_mode.single_description_summary(
            folder_path_output=folder_path_project,
            file_path_report_origin=file_path_report,
            dict_summary=dict_summary,
        )

        update_description_summary.main(
            path_summary_top,
            folder_path_project,
            document_hashtag,
            document_title,
        )

    # make header project
    header_maker(folder_path_project)

    # Check if has warnings
    has_warning = utils_timestamp.check_descriptions_warning(
        folder_path_project
    )
    if has_warning:
        input(
            '\nThere are warnings in the file "descriptions.xlsx".'
            + "Correct before the next step."
        )
    else:
        pass

    ################################### p6

    folder_script_path = utils.get_folder_script_path()
    path_file_config = os.path.join(folder_script_path, "config.ini")
    config = utils.get_config_data(path_file_config)
    dict_config = config

    print(f"\nProject: {folder_path_project}\n")

    tgsender.send_via_telegram_api(Path(folder_path_project), dict_config)

    # Post and Pin summary
    autopost_summary.run(folder_path_project)

    # Publish on moc
    path_file_moc_template = Path("user") / "moc_template.txt"
    send_to_moc(
        send_moc, moc_chat_id, path_file_moc_template, folder_path_project
    )

    clean_temp_files(autodel_video_temp, folder_path_project)


def get_list_project_path(root_folder_path):

    list_dir_name = os.listdir(root_folder_path)
    list_project_path = []
    for dir_name in list_dir_name:

        path_folder = os.path.join(root_folder_path, dir_name)
        if not os.path.isdir(path_folder):
            continue
        list_project_path.append(path_folder)
    return list_project_path


def main():
    """
    How to use
    -Place the folder of the 4 required repositories and this repository in
    the same location. Then there must be 5 folders in the same location
    -Enter the 'zimatise' folder and run the zimatise.py file
    -Follow the on-screen instructions
    -For more details, check the documentation for the required repositories
    Source: https://github.com/apenasrr/zimatise
    """

    # get config data
    folder_script_path = utils.get_folder_script_path()
    path_file_config = os.path.join(folder_script_path, "config.ini")
    config = utils.get_config_data(path_file_config)
    folder_path_start = config["folder_path_start"]
    file_size_limit_mb = int(config["file_size_limit_mb"])
    mode = config["mode"]
    max_path = int(config["max_path"])
    list_video_extensions = config["video_extensions"].split(",")
    duration_limit = config["duration_limit"]
    activate_transition = config["activate_transition"]
    start_index = int(config["start_index"])
    hashtag_index = config["hashtag_index"]
    reencode_plan = config["reencode_plan"]
    send_moc = int(config["send_moc"])
    moc_chat_id = int(config["moc_chat_id"])
    autodel_video_temp = int(config["autodel_video_temp"])

    descriptions_auto_adapt_str = config["descriptions_auto_adapt"]
    if descriptions_auto_adapt_str == "true":
        descriptions_auto_adapt = True
    else:
        descriptions_auto_adapt = False

    path_summary_top = config["path_summary_top"]
    path_summary_bot = config["path_summary_bot"]
    document_hashtag = config["document_hashtag"]
    document_title = config["document_title"]

    dict_summary = {}
    dict_summary["path_summary_top"] = Path("user") / path_summary_top
    dict_summary["path_summary_bot"] = Path("user") / path_summary_bot

    file_path_report = None
    folder_path_report = None
    utils.ensure_folder_existence(["projects"])

    while True:
        print(folder_path_start)
        list_project_path = get_list_project_path(folder_path_start)
        if len(list_project_path) == 0:
            time.sleep(5)
            continue
        for folder_path_report in list_project_path:
            file_path_report = vidtool.set_path_file_report(
                Path(folder_path_report)
            )
            run(
                folder_path_report,
                file_path_report,
                list_video_extensions,
                file_size_limit_mb,
                duration_limit,
                start_index,
                activate_transition,
                hashtag_index,
                dict_summary,
                descriptions_auto_adapt,
                path_summary_top,
                document_hashtag,
                document_title,
                reencode_plan,
                mode,
                send_moc,
                moc_chat_id,
                autodel_video_temp,
            )
        input("\nProject processed and sent to Telegram")
        vidtool.clean_cmd()


if __name__ == "__main__":
    logging_config()
    main()
