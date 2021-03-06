"""This is a simple GUI frontend to run the spatial/temporal analysis tools for GRACE
Tellus groundwater anomaly data.
Author: Arthur Elmes
2021-05-28"""

import PySimpleGUI as sg
import os.path
from datetime import datetime
import sys

# modules in this package
from grace import time_series_aoi
from grace import download_grace
from grace import viz_grace
from grace import img_diff


# example gui from https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Button_Func_Calls.py
def run_download(start, end, dl_dir):
    print('Now downloading GRACE images for time period.')
    download_grace.dl_data(dl_dir, start, end)


def run_vis(ul, lr, workspace):
    print('Now creating map of AOI.')
    viz_grace.make_all_plots(workspace, ul, lr)


def run_plots(start, end, csv, workspace):
    print('Now creating time series plots for AOI.')
    # for these graphs, must have full year of data
    if start.month != 1:
        start = datetime.strptime(str(start.year) + '-01-01', '%Y-%m-%d')
    if end.month != 1 or end.month != 12:
        end = datetime.strptime(str(end.year) + '-12-31', '%Y-%m-%d')

    time_series_aoi.make_time_series_plots(base_dir=workspace,
                                           prdct='GRD-3',
                                           start_date=start,
                                           end_date=end,
                                           csv_name=csv)


def make_img_diff(start, end, ul, lr, workspace):
    print('Now creating image difference map for AOI.')
    try:
        img_diff.run_img_diff(start, end, ul, lr, workspace)
    except IndexError:
        print('File(s) not found -- make sure you have a file for this date!')


def main():
    # # example gui from https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Button_Func_Calls.py

    # set theme
    sg.theme('Topanga')

    # set the layout bits
    data_entry_col = [
                        [sg.Text('Welcome to the GRACE Tellus Data eXplorer (GTX)!\n', font=('Lucinda', 24))],
                        [sg.Text('Instructions for use:\n'
                                 '1. Set your AOI bounding coords, time, sample CSV, and workspace.\n'
                                 '2. Click "Set date and AOI".\n'    
                                 'Finally, download your images, and run the analyses.\n'
                                 '\nNOTES: All variables must be set prior to clicking "Set date and AOI"!\n'
                                 'Format for lat/long coords is: 60 -120 '
                                 'for latitude 60N by longitude 120W.\n'
                                 'The sample CSV must look like 1,lat,lon with no headers.\n', font=('Lucinda', 14))],
                         [sg.Text('Start Date in YYYY-MM-DD', size=(30, 1), font=('Lucinda', 14)),
                          sg.InputText(key='-StartDate-', size=(15, 1), font=('Lucinda', 14))],
                         [sg.Text('End Date in YYYY-MM-DD', size=(30, 1), font=('Lucinda', 14)),
                          sg.InputText(key='-EndDate-', size=(15, 1), font=('Lucinda', 14))],
                         [sg.Text('Upper left corner latitude', size=(30, 1), font=('Lucinda', 14)),
                          sg.InputText(key='-ULLAT-', size=(15, 1), font=('Lucinda', 14))],
                         [sg.Text('Upper left corner longitude', size=(30, 1), font=('Lucinda', 14)),
                          sg.InputText(key='-ULLON-', size=(15, 1), font=('Lucinda', 14))],
                         [sg.Text('Lower right corner latitude', size=(30, 1), font=('Lucinda', 14)),
                          sg.InputText(key='-LRLAT-', size=(15, 1), font=('Lucinda', 14))],
                         [sg.Text('Lower right corner longitude', size=(30, 1), font=('Lucinda', 14)),
                          sg.InputText(key='-LRLON-', size=(15, 1), font=('Lucinda', 14))],
                         [sg.Text('Workspace:', size=(30, 1), font=('Lucinda', 14)),
                          sg.InputText(key='-WORKSPACE-', size=(35, 1), font=('Lucinda', 14))],
                        [sg.Text('Sample CSV (id,lat,lon):', size=(30, 1), font=('Lucinda', 14)),
                         sg.InputText(key='-SAMPLE-', size=(35, 1), font=('Lucinda', 14))],
                         [sg.Button('Set date and AOI', key='-Submit-', font=('Lucinda', 14))],
                        [sg.Button('Download Time Series', key='-Download-', font=('Lucinda', 14)),
                         sg.Button('Create AOI Maps', key='-Map-', font=('Lucinda', 14)),
                         sg.Button('Time Series Graphs', key='-Time-', font=('Lucinda', 14)),
                         sg.Button('MakeImage Difference', key='-ImDiff-', font=('Lucinda', 14))],
                      ]

    file_list_col = [
        [
            sg.Text('Image Folder', font=('Lucinda', 14)),
            sg.In(size=(25,1), enable_events=True, key='-FOLDER-'),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(40, 20), key='-FILE LIST-'
            )
        ],
    ]

    img_viewer_col = [
        [sg.Text('Run analysis and then choose an image from the list.', font=('Lucinda', 14))],
        [sg.Text(size=(40, 1), key='-TOUT-')],
        [sg.Image(key='-IMAGE-')],
    ]

    layout = [
        [
            sg.Column(data_entry_col),
            sg.VSeperator(),
            sg.Column(file_list_col),
            sg.VSeperator(),
            sg.Column(img_viewer_col)
        ]
    ]
    # make the window obj
    window = sg.Window('GRACE Data eXplorer Beta', layout)
    # base_dir = '/home/arthur/Dropbox/career/e84/sample_data/'
    # the event loop
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == '-Download-':
            run_download(date_start, date_end, base_dir)
            print(base_dir)
        elif event == '-Map-':
            run_vis(ul_coord, lr_coord, base_dir)
        elif event == '-Time-':
            run_plots(date_start, date_end, sample_csv, base_dir)
        elif event == '-ImDiff-':
            date_start_doy = download_grace.convert_date(date_start)
            date_end_doy = download_grace.convert_date(date_end)
            make_img_diff(date_start_doy, date_end_doy, ul_coord, lr_coord, base_dir)
        elif event == '-Submit-':
            date_start = datetime.strptime(values['-StartDate-'], '%Y-%m-%d')
            date_end = datetime.strptime(values['-EndDate-'], '%Y-%m-%d')
            ul_coord = (int(values['-ULLAT-']), int(values['-ULLON-']))
            lr_coord = (int(values['-LRLAT-']), int(values['-LRLON-']))
            base_dir = values['-WORKSPACE-']
            sample_csv = os.path.join(base_dir, values['-SAMPLE-'])
        elif event == '-FOLDER-':
            folder = values['-FOLDER-']
            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []
            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                   and f.lower().endswith(('.png', '.gif'))
            ]
            window['-FILE LIST-'].update(fnames)
        elif event == '-FILE LIST-':  # A file was chosen from the listbox
            try:
                filename = os.path.join(
                    values['-FOLDER-'], values['-FILE LIST-'][0]
                )
                window['-TOUT-'].update(filename)
                window['-IMAGE-'].update(filename=filename)
            except:
                pass

    window.close()


if __name__ == '__main__':
	main()

