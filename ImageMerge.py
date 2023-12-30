#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys
import shutil
from tkinter.constants import *
from PIL import Image
import string
import fnmatch
import configparser as ConfigParser
import wx

class ImageMerge:
    """Images merge single image"""
    __image_target = 0

    def __init__(self):
       self.__image_target = 0

    def GetImage(self):
        return self.__image_target
       
    def search_file(self,path,file_filter,contain_sub_path = False):
        target_file_paths = []
        target_file_names = []
        file_names = []
        file_names = os.listdir(path)
        for i in range(0, len(file_names)):
            file_path = os.path.join(path, file_names[i])
            if os.path.isdir(file_path):
                print('DIR Name:' + file_path)
                if contain_sub_path == True :
                    self.search_file(file_path, file_filter, contain_sub_path)
            else:
                print('File Name:' + file_names[i])
                if fnmatch.fnmatch(file_names[i],file_filter):
                    target_file_names.append(file_names[i])
                    print('File Path Name:' + file_path)
                    
        print(target_file_names)
        for file_name in target_file_names:
            target_file_paths.append(os.path.join(path, file_name))
            
        return target_file_paths
                    

    def read_file(self,paths,mode = 'r'):
        images = []
        print('read_file')
        for file_path in paths:
            try:
                images.append(Image.open(file_path,mode))
            except:
                 print('read file error:', file_path)

        print('read_file finished')
        return images
    
    def merge(self,images,h_frame_count, v_frame_count, image_format = 'RGBA'):

        image_count = len(images)
        single_width = 0
        single_height = 0

        if image_count != 0 :
            single_width = images[0].size[0]
            single_height = images[0].size[1]
        else:
            print("merge error!")
            return
        
        print('image merge')
        target_size = (single_width*h_frame_count,single_height*v_frame_count)
        if self.__image_target == 0 :
            self.__image_target = Image.new(image_format,target_size)
        elif self.__image_target.size != target_size :
            del self.__image_target
            self.__image_target = Image.new(image_format,target_size)
            
        print('merge iamge size:',self.__image_target.size)

        for i in range(0,v_frame_count):
            for j in range(0,h_frame_count):
                if i*h_frame_count+j < len(images):
                    image = images[i*h_frame_count+j]
                    image_box = (image.size[0]*j,image.size[1]*i,image.size[0]*j+image.size[0],image.size[1]*i+image.size[1])
                    self.__image_target.paste(image,image_box)
                else:
                    break

        print("merge finished!")

    def save(self,path):
        print('save file path:'+ path)
        if self.__image_target != 0 :
            self.__image_target.save(path)
        print("save finished!")

class Configure:
    """Image merge configure"""
    
    def __init__(self):
        self.__config = ConfigParser.ConfigParser()
        self.search_dir = 'd:\\image'
        self.file_filter = '*.png'
        self.save_file_dir = 'd:\\image'
        self.save_file_name = 'merge.png'
        self.merge_mode = 0
        self.merge_h_count = 1
        self.merge_v_count = 1

    def read(self,path):
        try:
            self.__config.readfp(open(path,'r'))
        except:
            print("read error!")
            return False

        if not self.__config.has_section("Options"):
            return False
        
        if self.__config.has_option("Options","search_dir"):
            self.search_dir = self.__config.get("Options","search_dir")

        if self.__config.has_option("Options","file_filter"):
            self.file_filter = self.__config.get("Options","file_filter")
            
        if self.__config.has_option("Options","save_file_dir"):
            self.save_file_dir = self.__config.get("Options","save_file_dir")
            
        if self.__config.has_option("Options","save_file_name"):
            self.save_file_name = self.__config.get("Options","save_file_name")
            
        if self.__config.has_option("Options","merge_mode"):
            self.merge_mode = self.__config.getint("Options","merge_mode")
            
        if self.__config.has_option("Options","merge_h_count"):
            self.merge_h_count = self.__config.getint("Options","merge_h_count")
            
        if self.__config.has_option("Options","merge_v_count"):
            self.merge_v_count = self.__config.getint("Options","merge_v_count")

        return True

    def write(self,path):
        if not self.__config.has_section("Options"):
            self.__config.add_section("Options")

        self.__config.set("Options", "search_dir", self.search_dir)
        self.__config.set("Options", "file_filter", self.file_filter)
        self.__config.set("Options", "save_file_dir", self.save_file_dir)
        self.__config.set("Options", "save_file_name", self.save_file_name)
        self.__config.set("Options", "merge_mode", self.merge_mode)
        self.__config.set("Options", "merge_h_count", self.merge_h_count)
        self.__config.set("Options", "merge_v_count", self.merge_v_count)

        try:
            self.__config.write(open(path,'w'))
        except:
            print("wirte error!")
            return False
        
        return True


class FileDropTarget(wx.FileDropTarget):
    
    def __init__(self, window):  
        wx.FileDropTarget.__init__(self)  
        self.window = window  
  
    def OnDropFiles(self,  x,  y, fileNames):

        if len(fileNames) > 0:
            fileNames.sort()
        self.window.lbFilePath.Clear()
        del self.window.file_drop_paths
        self.window.file_drop_paths = []
        for fileName in fileNames:
            if os.path.isfile(fileName):
                if fnmatch.fnmatch(fileName,self.window.config.file_filter):
                    self.window.lbFilePath.Append(fileName)
                    self.window.file_drop_paths.append(fileName)
        return True

class DrawPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        self.draw_image = None

    def SetImage(self, image):
        self.draw_image = image
        self.Refresh()

    def OnPaint(self, event):
       
        dc = wx.PaintDC(self)
        dc = wx.BufferedDC(dc)
        dc.SetBackground(wx.Brush("WHITE"))
        dc.Clear()
        
        dc.SetBrush(wx.Brush("GREY", wx.CROSSDIAG_HATCH))
        windowsize= self.GetClientSize()
        dc.DrawRectangle(0, 0, windowsize[0], windowsize[1])

        if self.draw_image != None:
            image_width = self.draw_image.GetWidth()
            image_height = self.draw_image.GetHeight()
            bmp = self.draw_image
            if image_width >  windowsize[0] or image_height >  windowsize[1]:
                scale_width = image_width
                scale_height = image_height
                if image_width >  windowsize[0] and image_height >  windowsize[1]:
                    scale_width = windowsize[0]
                    scale_height = windowsize[1]
                elif image_width >  windowsize[0]:
                    scale_width = image_width*windowsize[0]/image_width
                    scale_height = image_height*windowsize[0]/image_width
                elif image_height >  windowsize[1]:
                    scale_width = image_width*windowsize[1]/image_height
                    scale_height = image_height*windowsize[1]/image_height
                else:
                    pass
                image = self.draw_image.ConvertToImage().Scale(int(scale_width),int(scale_height))
                bmp = image.ConvertToBitmap()
                
            if "gtk1" in wx.PlatformInfo:
                img = bmp.ConvertToImage()
                img.ConvertAlphaToMask(220)
                bmp = img.ConvertToBitmap()

            dc.DrawBitmap(bmp,0,0,True)
            
    
    def OnEraseBackground(self, event):
        pass

class MainFrame(wx.Frame):
    """window show"""

    
    def __init__(self):
        wx.Frame.__init__(self,parent=None,id=-1,title = u'图像合成', size = (960,600))

        self.file_drop_paths = []
        
        #读配置文件
        self.config_file_name = "Configure.ini"
        self.config = Configure()
        try:
            self.config.read(self.config_file_name)
        except:
            print("read configure error!")
            
        #创建控件
        panel = wx.Panel(self)
        xpos = 10
        ypos = 10
        label = wx.StaticText(panel,label=u"合成图像路径:",pos=(xpos,ypos+4))
        
        xpos += label.GetSize().GetWidth()+6
        self.textSearchDir = wx.TextCtrl(panel, pos = (xpos, ypos+2),size =(306, 26))
        self.textSearchDir.SetValue(self.config.search_dir)
        self.Bind(wx.EVT_TEXT, self.OnTextChangePath, self.textSearchDir)
        
        xpos += self.textSearchDir.GetSize().GetWidth()+6
        btn_open = wx.Button(panel,label=u"浏览",pos=(xpos,ypos))
        self.Bind(wx.EVT_BUTTON,self.OnClickedOpen, btn_open)

        xpos = 10
        ypos += 30
        label = wx.StaticText(panel,label=u"图像文件过滤:",pos=(xpos,ypos+4))

        FileFilter = ['*.png','*.jpg','*.jpeg','*.bmp']
        xpos += label.GetSize().GetWidth()+6
        self.comboFileFilter = wx.ComboBox(panel, value='*.png', pos = (xpos, ypos+2),size =(100, 26),choices=FileFilter,style=wx.CB_DROPDOWN)
        self.comboFileFilter.SetValue(self.config.file_filter)
        self.Bind(wx.EVT_TEXT, self.OnTextChangeFilter, self.comboFileFilter)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnterFilter, self.comboFileFilter)
        self.Bind(wx.EVT_COMBOBOX, self.OnComboBoxSelected, self.comboFileFilter)


        xpos = 10
        ypos += 30
        label = wx.StaticText(panel,label=u"合成模式:",pos=(xpos,ypos+4))
        
        self.merge_mode_group = []

        xpos += label.GetSize().GetWidth()+6
        radio1 = wx.RadioButton(panel,label=u"水平模式",pos=(xpos,ypos+4),style=wx.RB_GROUP)
        
        xpos += radio1.GetSize().GetWidth()+6
        radio2 = wx.RadioButton(panel,label=u"垂直模式",pos=(xpos,ypos+4))
        
        xpos += radio2.GetSize().GetWidth()+6
        radio3 = wx.RadioButton(panel,label=u"自由模式",pos=(xpos,ypos+4))

        xpos = 10
        ypos += 30
        label = wx.StaticText(panel,label=u"水平合成数:",pos=(xpos,ypos+4))

        xpos += label.GetSize().GetWidth()+6
        spinHMergeCount = wx.SpinCtrl(panel, value="", pos=(xpos,ypos+2))
        spinHMergeCount.SetRange(1,100)
        spinHMergeCount.SetValue(self.config.merge_h_count)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpinSelected, spinHMergeCount)
        self.Bind(wx.EVT_TEXT, self.OnSpinTextChange, spinHMergeCount)
        self.spinHMergeCount = spinHMergeCount

        xpos += spinHMergeCount.GetSize().GetWidth()+6
        label = wx.StaticText(panel,label=u"垂直合成数:",pos=(xpos,ypos+4))

        xpos += label.GetSize().GetWidth()+6
        spinVMergeCount = wx.SpinCtrl(panel, value="", pos=(xpos,ypos+2))
        spinVMergeCount.SetRange(1,100)
        spinVMergeCount.SetValue(self.config.merge_v_count)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpinSelected, spinVMergeCount)
        self.Bind(wx.EVT_TEXT, self.OnSpinTextChange, spinVMergeCount)
        self.spinVMergeCount = spinVMergeCount

        self.merge_mode_group.append((radio1,(spinHMergeCount,spinVMergeCount)))
        self.merge_mode_group.append((radio2,(spinHMergeCount,spinVMergeCount)))
        self.merge_mode_group.append((radio3,(spinHMergeCount,spinVMergeCount)))

        for radio,spins in self.merge_mode_group:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioGroupSelected, radio )

        radio_default_selected = None
        if self.config.merge_mode == 0:
            radio_default_selected = radio1
        elif self.config.merge_mode == 1:
            radio_default_selected = radio2
        else:
            radio_default_selected = radio3

        for radio, spins in self.merge_mode_group:
            if radio is radio_default_selected:
                radio.SetValue(True)
                for spin in spins:
                    spin.Enable(True)
            else:
                for spin in spins:
                    spin.Enable(False)

        xpos = 10
        ypos += 30
        label = wx.StaticText(panel,label=u"图像合成保存目录:",pos=(xpos,ypos+4))

        xpos += label.GetSize().GetWidth()+6
        self.textSaveFileDir = wx.TextCtrl(panel, pos = (xpos, ypos+2),size =(280, 26))
        self.textSaveFileDir.SetValue(self.config.save_file_dir)
        self.Bind(wx.EVT_TEXT, self.OnTextChangeSaveFileDir, self.textSaveFileDir)

        xpos += self.textSaveFileDir.GetSize().GetWidth()+6
        btn_save = wx.Button(panel,label=u"保存",pos=(xpos,ypos))
        self.Bind(wx.EVT_BUTTON,self.OnClickedSave, btn_save)
        
        xpos = 10
        ypos += 30
        label = wx.StaticText(panel,label=u"图像合成保存文件名称:",pos=(xpos,ypos+4))

        xpos += label.GetSize().GetWidth()+6
        self.textSaveFileName = wx.TextCtrl(panel, pos = (xpos, ypos+2),size =(200, 26))
        self.textSaveFileName.SetValue(self.config.save_file_name)
        self.Bind(wx.EVT_TEXT, self.OnTextChangeSaveFileName, self.textSaveFileName)

        xpos += self.textSaveFileName.GetSize().GetWidth()+6
        btnExecuteImageMerge = wx.Button(panel,label=u"执行图像合成",pos=(xpos,ypos))
        btnExecuteImageMerge.SetBackgroundColour('Yellow')
        self.Bind(wx.EVT_BUTTON,self.OnClickedExecuteImageMerge, btnExecuteImageMerge)

        xpos += btnExecuteImageMerge.GetSize().GetWidth()+6
        btnClearFileList = wx.Button(panel,label=u"清理文件列表",pos=(xpos,ypos))
        btnClearFileList.SetBackgroundColour('Yellow')
        self.Bind(wx.EVT_BUTTON,self.OnClickedClearFileList, btnClearFileList)

        xpos = 10
        ypos += 30
        border = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(border)
        
        box = wx.StaticBox(panel, label=u"图像文件")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        border.Add(bsizer, 0, wx.TOP|wx.EXPAND, ypos)

        self.lbFilePath = wx.ListBox(panel,size=(532,200),style=wx.LB_EXTENDED)
        bsizer.Add(self.lbFilePath,1,wx.ALL|wx.EXPAND,0)
        dropTarget = FileDropTarget(self)
        self.SetDropTarget(dropTarget)

        box = wx.StaticBox(panel, label=u"图像显示")
        border2 = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        border.Add(border2, 1, wx.TOP|wx.LEFT|wx.EXPAND, 6)
        
        self.image_show = DrawPanel(box)
        border2.Add(self.image_show,1,wx.TOP|wx.EXPAND, 0)
        


    def __del__(self):
        #写配置
        try:
            self.config.write(self.config_file_name)
        except:
            print("write configure error!")

    def OnQuit(self, event):
        self.Close()

    def OnClickedOpen(self, event):
        dlg = wx.DirDialog(self,u"请选择合成图片的路径：",style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            if len(dlg.GetPath()) > 0:
                self.textSearchDir.SetValue(dlg.GetPath())
                self.config.search_dir = dlg.GetPath()
            
        dlg.Destroy()

    def OnTextChangePath(self, event):
        self.config.search_dir = event.GetString()

    def OnTextChangeFilter(self, event):
        self.config.file_filter = event.GetString()

    def OnTextEnterFilter(self, event):
        self.config.file_filter = event.GetString()

    def OnComboBoxSelected(self, event):
        self.config.file_filter = event.GetString()

    def OnRadioGroupSelected(self, event):
        radio_selected = event.GetEventObject()

        for radio, spins in self.merge_mode_group:
            if radio is radio_selected:
                self.config.merge_mode = self.merge_mode_group.index((radio,spins))
            
            if radio is radio_selected:
                for spin in spins:
                    spin.Enable(True)
            else:
                for spin in spins:
                    spin.Enable(False)

                    
    def OnSpinSelected(self, event):
        spin = event.GetEventObject()
        if spin is self.spinHMergeCount:
            self.config.merge_h_count = spin.GetValue()
        elif spin is self.spinVMergeCount:
            self.config.merge_v_count = spin.GetValue()
            

    def OnSpinTextChange(self, event):
        spin = event.GetEventObject()

        if spin is self.spinHMergeCount:
            self.config.merge_h_count = spin.GetValue()
        elif spin is self.spinVMergeCount:
            self.config.merge_v_count = spin.GetValue()

    def OnTextChangeSaveFileDir(self, event):
        self.config.save_file_dir = event.GetString()

    def OnTextChangeSaveFileName(self, event):
        self.config.save_file_name = event.GetString()

    def OnClickedSave(self, event):
        dlg = wx.DirDialog(self,u"请选择合成图片的保存目录：",style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            if len(dlg.GetPath()) > 0:
                self.textSaveFileDir.SetValue(dlg.GetPath())
                self.config.save_file_dir = dlg.GetPath()
            
        dlg.Destroy()

    def OnClickedClearFileList(self, event):
        self.lbFilePath.Clear()
        del self.file_drop_paths
        self.file_drop_paths = []
        
        
    def OnClickedExecuteImageMerge(self, event):

        print(self.file_drop_paths)
        print(self.config.search_dir)
        save_file_path = os.path.join(self.config.save_file_dir,self.config.save_file_name)

        if len(self.file_drop_paths) == 0:
            if os.path.exists(self.config.search_dir) == False:
                wx.MessageBox(u"输入合成图像的目录不存在！",u"错误",wx.OK|wx.ICON_ERROR)
                return
            else:
                if not os.path.exists(self.config.save_file_dir) or len(self.config.save_file_name) == 0  or len(os.path.splitext(save_file_path)[1]) == 0 :
                    wx.MessageBox(u"保存合成图像路径出错，请重新输入！",u"错误",wx.OK|wx.ICON_ERROR)
                    return
            
        try:
            obj = ImageMerge()
            sort_paths = None
            if len(self.file_drop_paths) == 0:
                paths = obj.search_file(self.config.search_dir,self.config.file_filter,False)
                sort_paths = self.file_names_sort(paths)
                self.lbFilePath.Clear()
                for file_path in sort_paths:
                    self.lbFilePath.Append(file_path)
            else:
                sort_paths = self.file_names_sort(self.file_drop_paths)
            
            if sort_paths != None and len(sort_paths) > 0:
                images = obj.read_file(sort_paths)

                if len(images) > 0:
                    save_image_format = 'RGB'
                    file_ext = os.path.splitext(save_file_path)[1]
                    
                    if file_ext == '.png' or file_ext == '.jpeg' or file_ext == '.jpg':
                        save_image_format = 'RGBA'
                    else:
                        save_image_format = 'RGB'

                    if self.config.merge_mode == 0:
                        merge_h_count = len(images)
                        obj.merge(images,merge_h_count,1,save_image_format)
                    elif self.config.merge_mode == 1:
                        merge_v_count = len(images)
                        obj.merge(images,1,merge_v_count,save_image_format)
                    else:
                        obj.merge(images,self.config.merge_h_count,self.config.merge_v_count,save_image_format)
               
                    try:
                        obj.save(save_file_path)
                    except:
                        wx.MessageBox(u"保存合成图像出错！",u"错误",wx.OK|wx.ICON_ERROR)
                        return
                    
                else:
                    wx.MessageBox(u"没有读取到要合成的图片文件内容。",u"温馨提示")
                    return 
            else:
                wx.MessageBox(u"没有找到合成的图片文件。",u"温馨提示")
                return
            
        except:
            wx.MessageBox(u"图像合成出错！",u"错误",wx.OK|wx.ICON_ERROR)
            return

        show_image = wx.Bitmap(save_file_path)
        self.image_show.SetImage(show_image)
        msg_text = u"图像合成完成，保存在："+save_file_path
        wx.MessageBox(msg_text,u"温馨提示")

    def file_names_sort(self, paths):

        if len(paths) > 0:
            paths.sort()

        return paths
        

class ImageMergeApp(wx.App):  

    def OnInit(self):
        frame = MainFrame()
        frame.Show(True)
        return True


def main():
    """software start runing """
    
    app = ImageMergeApp()  
    app.MainLoop()
    
    return

									
if __name__ == '__main__':
    main()

        
