# -*- coding: utf-8 -*-
'''
Created on 05/10/2009

@author: Federico Cáceres <fede.caceres@gmail.com>

Implements a wizard style similar to Microsoft Aero Wizard specification.
'''

import wx
import wx.lib.newevent
from time import sleep

(PageChangeEvent, EVT_PAGE_CHANGE) = wx.lib.newevent.NewEvent()

BUTTON_LABELS = {
    'next' : u'Siguiente',
    'prev' : u'Anterior',
    'cancel' : u'Cancelar',
    'end' : u'Finalizar',
}

EXIT_DIALOG = {
    'title' : u'Confirmación de salida',
    'body' : u'Esto anulará los cambios sobre su archivo de datos.\n¿Está seguro de que desea salir?'
}

class AeroWizard(wx.Frame):
    '''
    AeroWizard class
    Description? Nah...
    '''
    def __init__(self, title, data = None):
        wx.Frame.__init__(self, None, -1, title, style= wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX))
        self.data = data
        self.pages = []
        self.start_page = None
        self.current_page = None
        self.route = 'default'
        self.on_exit_confirm = True
        
        self.DoLayout()
        self.Bind(EVT_PAGE_CHANGE, self.OnPageChange)
    
    def DoLayout(self):
        '''
        Set the basic layout consisting of a white frame, a root vertical BoxSizer,
        which in turn contains another vertical box sizer where wizard pages are appended
        and a button bar on the bottom
        '''
        self.SetBackgroundColour("#ffffff")
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        # create content panel for wizard pages
        self.content = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.content, 1, wx.EXPAND)
        # buttons!
        buttons = self.CreateButtons()
        sizer.Add(buttons, 0, wx.EXPAND)

    def CreateButtons(self):
        '''Create the lower buttons and bind their events'''
        panel = wx.Panel(self)
        panel.SetBackgroundColour("#f0f0f0")
        
        self.button_prev = wx.Button(panel, wx.ID_PREVIEW_PREVIOUS, BUTTON_LABELS['prev'])
        self.button_next = wx.Button(panel, wx.ID_PREVIEW_NEXT, BUTTON_LABELS['next'])
        self.button_end = wx.Button(panel, wx.ID_CLOSE, BUTTON_LABELS['cancel'])
        
        self.Bind(wx.EVT_BUTTON, self.OnButtonPrev, self.button_prev)
        self.Bind(wx.EVT_BUTTON, self.OnButtonNext, self.button_next)
        self.Bind(wx.EVT_BUTTON, self.OnButtonEnd, self.button_end)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        
        sizer.AddStretchSpacer(1)
        sizer.Add(self.button_prev, 0, wx.ALL, 7)
        sizer.Add(self.button_next, 0, wx.ALL, 7)
        sizer.Add(self.button_end, 0, wx.ALL, 7)

        return panel
    
    def UpdateButtons(self):
        '''
        Refresh buttons to change their enabled/disabled states of the next and prev buttons
        and the text for the cancel/finish button
        '''
        # enable next/prev if GetNext/GetPrev return something!
        self.button_next.Enable(True if self.current_page.GetNext() else False)
        self.button_prev.Enable(True if self.current_page.GetPrev() else False)
        # if this page is the end, present the end button, if not, there are more to come just present the cancel label
        if self.current_page.is_end:
            self.button_end.SetLabel(BUTTON_LABELS['end'])
            self.on_exit_confirm = False
        else:
            self.button_end.SetLabel(BUTTON_LABELS['cancel'])
            self.on_exit_confirm = True
        self.Refresh()
        
    def RunWizzard(self, app = None):
        app = wx.GetApp()
        app.TopWindow = self
        app.TopWindow.Show()
        wx.PostEvent(self, PageChangeEvent(page=self.start_page))
        app.MainLoop()
    
    def OnPageChange(self, event):
        #page = event.page(self, self.data)
        page = event.page

        if page == None:
            return
        # hide and detach current page from wizard
        if self.current_page:
            self.current_page.Show(False)
            self.content.Detach(self.current_page)
        # set new page, attach it to the wizard and show it
        self.current_page = page
        self.content.Add(self.current_page)
        self.current_page.Show(True)
        # update buttons
        self.UpdateButtons()        
        #print "AFTER 1", self.GetSizer().GetMinSize(), self.GetVirtualSize()

        """  
        delay = 30
        frames = 100
        source = self.GetVirtualSize()
        target = self.GetSizer().GetMinSize()
        steps = [0,0]
        steps[0] = target[0] - source[0]
        steps[1] = target[1] - source[1]
        new_size = self.GetVirtualSize()
        for frame in xrange(frames):
            new_size[0] += steps[0]
            new_size[1] += steps[1]
            self.SetVirtualSize(new_size)
            self.Center()
            sleep(1)
        """
        
        # autoadjust to content and center
        self.content.Layout() # distribute the window's new content
        self.Fit() # fit the size of the wizard window
        self.Center() # center :P
        
        
        """
        dialog = wx.MessageDialog(None, "!!!", "!!!", wx.OK)
        dialog.ShowModal()
        dialog.Destroy()
        """
        
    def SetStartPage(self, page):
        '''Set the start page'''
        self.start_page = page

    def AddPage(self, page):
        self.pages.append(page)
        
    def OnButtonEnd(self, event):
        if self.on_exit_confirm:
            dialog = wx.MessageDialog(self, EXIT_DIALOG['body'], EXIT_DIALOG['title'], wx.YES_NO | wx.ICON_QUESTION)
            if dialog.ShowModal() == wx.ID_YES:
                self.Close()
        else:
            self.Close()

    def OnButtonPrev(self, event):
        wx.PostEvent(self, PageChangeEvent(page=self.current_page._GetPrevOrDefault()))
        
    def OnButtonNext(self, event):
        wx.PostEvent(self, PageChangeEvent(page=self.current_page._GetNextOrDefault()))

class AeroPage(wx.Panel):
    '''AeroWizard Page'''
    def __init__(self, parent, title):
        wx.Panel.__init__(self, parent, -1, (-1, -1))
        self.wizard = parent
        self.title = title
        self.is_end = False
        self.items = []
        self.next = {}
        self.prev = {}
        self.SetBackgroundColour("#ffffff")
        self._aero_layout()
        self.Show(False)
        
    def _aero_layout(self):
        margin = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(margin)
        margin.AddSpacer(38)
        self.content = self.makePageTitle(self.title)
        margin.Add(self.content, 1, wx.EXPAND)
        margin.AddSpacer(38)
        for i in self.items:
            self.content.Add(i[0], i[1], i[2], i[3])
        
    def makePageTitle(self, title):
        sizer = wx.BoxSizer(wx.VERTICAL)
        #self.SetSizer(sizer)
        title = wx.StaticText(self, -1, title)
        title.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Segoe UI"))
        #title.SetForegroundColour("#1370AB")
        title.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HOTLIGHT))
        
        sizer.Add(title, 0, wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM, 19)
        return sizer
    
    def Add(self, item, proportion, flag, border):
        '''Add widgets to page'''
        self.items.append((item, proportion, flag, border))
    
    def GetNext(self):
        '''Override this method if you please'''
        return self._GetNextOrDefault()
    
    def GetPrev(self):
        '''Override this method if you please'''
        return self._GetPrevOrDefault()
    
    def _GetNextOrDefault(self):
        try:
            return self.next[self.wizard.route]
        except:
            try:
                return self.next['default']
            except:
                return None

    def _GetPrevOrDefault(self):
        try:
            return self.prev[self.wizard.route]
        except:
            try:
                return self.prev['default']
            except:
                return None

    def GoToNext(self):
        if self.next:
            wx.PostEvent(self.Parent, PageChangeEvent(page=self._GetNextOrDefault()))
    
    def GoToPrev(self):
        if self.prev:
            wx.PostEvent(self.Parent, PageChangeEvent(page=self._GetPrevOrDefault()))
            
    def Chain(self, target):
        '''
        Set the pages that will be chained with this one.
        Target can either be a AeroPage instance or a dictionary with the following format:
        {"route_name" : <instance of AeroPage>, "route2_name" : <instance of AeroPage>, ... }
        '''
        # if is dict, iterate over dict
        if isinstance(target, dict):
            for path_label, page in target.iteritems():
                self.next[path_label] = page # set forward route
                page.prev[path_label] = self # set backwards route
        # if is single page instance, set default route
        elif isinstance(target, AeroPage):
            self.next['default'] = target # forward
            target.prev['default'] = self # backwards
        else:
            raise TypeError("'target' argument should be of type 'dict' or type 'AeroPage'")

class AeroStaticText(wx.StaticText):
    '''StaticText with custom font for AeroWizard'''
    def __init__(self, parent, id, text):
        wx.StaticText.__init__(self, parent, id, text)
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Segoe UI"))