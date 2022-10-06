import improved_update_description as update_description
import update_summary


def main(path_summary_top, folder_path_output, document_hashtag,
         document_title, folder_path_input, **kwargs):

    list_file_path_zip = \
        update_description.get_list_file_path_zip(folder_path_output)


    if 'alternative_mode' in kwargs:
        alternative_mode = kwargs.get('alternative_mode')
        list_pdf_file_path = \
            update_description.get_list_files_path(
                folder_path_input, 
                pattern='.*([pP][dD][fF])'
            )
        if len(list_pdf_file_path) and alternative_mode:

            if alternative_mode == 1: 
                update_description.descriptions_report_update_with_docs(
                    folder_path_output,
                    list_pdf_file_path,
                    sort=True
                )
            elif alternative_mode == 2:
                update_description.descriptions_report_update_with_docs(
                    folder_path_output,
                    list_pdf_file_path,
                    sort=True
                )
                return

    count_file_path_zip = len(list_file_path_zip)
    if count_file_path_zip == 0:
        return

    update_description.descriptions_report_update_with_docs(folder_path_output,
                                                            list_file_path_zip,
                                                            document_hashtag,
                                                            axis=0)
    count_file_path_zip = len(list_file_path_zip)
    update_summary.summary_text_update_with_docs(count_file_path_zip,
                                                 path_summary_top,
                                                 folder_path_output,
                                                 document_hashtag,
                                                 document_title,
                                                 )
