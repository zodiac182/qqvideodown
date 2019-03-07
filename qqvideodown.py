#! /usr/bin/env python
# -*- coding:utf-8 -*-
from Tkinter import *
import ttk
import threading
import json
import requests

tecent_template_url = 'http://vv.video.qq.com/getinfo?vids=%s&platform=101001&otype=json&defn=shd&charge=0'
#tecent_template_url = 'http://vv.video.qq.com/getinfo?vids=%s&platform=101001&otype=json&defn=mp4&charge=0'

def tecent_parse(target_url):
    vid = target_url[len('https://v.qq.com/x/page/'):-5]
    v_info_url = requests.get(tecent_template_url % vid)
    v_info = v_info_url.content.decode('utf-8')
    json_data = v_info[len('QZOutputJson='):-1]
    json_obj = json.loads(json_data)
    for vi in json_obj['vl']['vi'][0]['ul']['ui']:
        download_url = vi['url'] + json_obj['vl']['vi'][0]['fn'] + '?vkey=' + \
                    json_obj['vl']['vi'][0]['fvkey']
    # download_url = json_obj['vl']['vi'][0]['ul']['ui'][0]['url'] + json_obj['vl']['vi'][0]['fn'] + '?vkey=' + \
    #                json_obj['vl']['vi'][0]['fvkey']
        print download_url
    video_name = json_obj['vl']['vi'][0]['ti'] + "." + json_obj['fl']['fi'][1]['name']
    return download_url, video_name


def down(download_url, video_name, func):
    r = requests.get(download_url, stream=True)
    length = float(r.headers['Content-Length'])
    t = 0
    with open(video_name, 'wb') as f:
        for trunk in r.iter_content(chunk_size=1024*1024):
            f.write(trunk)
            t = t + len(trunk)
            func('%s  %.2f%%' % (video_name, (t * 100 / length)))


class App(ttk.Frame):
    def __init__(self, parent=None, *args, **kwargs):
        self.parent = parent
        self.drawUI()
        self.video_per = ''

    def drawUI(self):
        ''' frame 1'''
        self.frame_a = Frame(self.parent)
        self.frame_a.grid(row=0, column=0, padx=1, pady=1, sticky='NSWE')

        Grid.columnconfigure(self.frame_a, 0, weight=1)

        self.new_url = StringVar()
        #self.new_url.set('https://v.qq.com/x/page/v0029l41udq.html')
        self.entry_url = Entry(
            self.frame_a, textvariable=self.new_url)
        self.entry_url.grid(row=0, column=0, padx=5, pady=5, columnspan=2, sticky='NWSE')

        self.btn_start = Button(self.frame_a, text=u"下载", command=self.start_click)
        self.btn_start.grid(row=0, column=1, padx=5, pady=5, sticky='NWSE')

        '''frame 2'''
        self.frame_b = Frame(self.parent)
        self.frame_b.grid(row=1, column=0, padx=1, pady=1, sticky='NSWE')

        self.frame_c = Frame(self.parent)
        self.frame_c.grid(row=2, column=0, padx=1, pady=1, sticky='NSWE')

        Grid.columnconfigure(self.frame_b, 0, weight=1)

        self.info_panel = ttk.LabelFrame(self.frame_b, text=u"正在下载")
        self.info_panel.grid(column=0, row=1, padx=5, pady=0, sticky='NWSE')

        Grid.columnconfigure(self.info_panel, 0, weight=1)
        Grid.rowconfigure(self.frame_c, 0, weight=1)
        Grid.columnconfigure(self.frame_c, 0, weight=1)

        self.txt_per = StringVar()
        self.lb_per = Label(self.info_panel, textvariable=self.txt_per)
        self.lb_per.grid(row=0, column=0, pady=0, columnspan=2, sticky='W')

        '''frame 3'''
        self.done_panel = ttk.LabelFrame(self.frame_c, text=u"完成列表")
        self.done_panel.grid(column=0, row=0, padx=5, pady=0, sticky='NWSE')
        Grid.columnconfigure(self.done_panel, 0, weight=1)
        Grid.rowconfigure(self.done_panel, 0, weight=1)

        self.download_list = Listbox(self.done_panel, selectmode=EXTENDED, bg='#FFFFFF')
        self.download_list.grid(row=0, column=0, padx=1, pady=1, sticky='NSWE')

        self.btn_clear = Button(self.frame_c, text=u"清空列表", command=self.clear_click)
        self.btn_clear.grid(row=1, column=0, padx=5, pady=5)

        # ----vertical scrollbar------------
        self.vbar = ttk.Scrollbar(
            self.done_panel, orient=VERTICAL, command=self.download_list.yview)
        self.download_list.configure(yscrollcommand=self.vbar.set)
        self.vbar.grid(row=0, column=1, sticky='NS')

    def clear_click(self):
        self.download_list.delete(0, END)

    def start_click(self):
        p = threading.Thread(target=self.download_process)
        p.setDaemon(True)
        p.start()

    def download_process(self):
        url = self.new_url.get()
        self.new_url.set('')
        if 'https://v.qq.com/x/page/' in url:
            download_url, video_name = tecent_parse(url)

            def _update_speed(per):
                self.txt_per.set(per)

            down(download_url, video_name, _update_speed)
            self.download_list.insert(END, video_name)


if __name__ == '__main__':
    root = Tk()
    app = App(parent=root)
    root.geometry('480x320')
    root.title(u'QQ视频下载')
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)
    root.mainloop()
