# -*- coding: utf-8 -*-
'''
Created on 05/10/2009

@author: Federico Cáceres <fede.caceres@gmail.com>
'''

import wx
import wx.lib.newevent
from time import sleep

(PageChangeEvent, EVT_PAGE_CHANGE) = wx.lib.newevent.NewEvent()

class AeroWizard(wx.Frame):
    def __init__(self, title, data = None):
        wx.Frame.__init__(self, None, -1, title, style= wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX))
        #wx.Frame.__init__(self, None, -1, title)
        self.data = data
        self.pages = []
        self.current_page = None
        
        self.DoLayout()
        self.Bind(EVT_PAGE_CHANGE, self.OnPageChange)
    
    def DoLayout(self):
        self.SetBackgroundColour("#ffffff")
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        # crear panel contender de los contenidos (valga la redundancia)
        self.content = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.content, 1, wx.EXPAND)

        # crear la botonera
        buttons = self.CreateButtons()
        sizer.Add(buttons, 0, wx.EXPAND)

    def CreateButtons(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour("#f0f0f0")
        
        self.button_prev = wx.Button(panel, wx.ID_PREVIEW_PREVIOUS, "Anterior")
        self.button_next = wx.Button(panel, wx.ID_PREVIEW_NEXT, "Siguiente")
        self.button_end = wx.Button(panel, wx.ID_CLOSE, "Cancelar")
        
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
        self.button_next.Enable(True if self.current_page.GetNext() else False)
        self.button_prev.Enable(True if self.current_page.GetPrev() else False)
        if self.current_page.is_end:
            self.button_end.SetLabel("Finalizar")
        else:
            self.button_end.SetLabel("Cancelar")
        self.Refresh()
        
    def RunWizzard(self, app = None):
        app = wx.GetApp()
        app.TopWindow = self
        app.TopWindow.Show()
        wx.PostEvent(self, PageChangeEvent(page=self.pages[0]))
        app.MainLoop()
    
    def OnPageChange(self, event):
        #page = event.page(self, self.data)
        page = event.page

        #print "BEFORE", self.GetSizer().GetMinSize(), self.GetVirtualSize()

        if page == None:
            return
        if self.current_page:
            self.current_page.Show(False)
            self.content.Detach(self.current_page)
        self.current_page = page
        self.current_page.Show(True)
        
        self.UpdateButtons()
        self.content.Add(page)
        
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
        
        self.content.Layout() # distribuir el nuevo contenido en la ventana
        self.Fit() # reajustar el tamaño de la ventana del wizard
        self.Center() # centrar
        
        
        
        #print "AFTER 2", self.GetSizer().GetMinSize(), self.GetVirtualSize()
        
        """
        page.Layout()
        page.Fit()
        page.Refresh()
        """
        
        """
        dialog = wx.MessageDialog(None, "!!!", "!!!", wx.OK)
        dialog.ShowModal()
        dialog.Destroy()
        """
        
    def AddPage(self, page):
        self.pages.append(page)
        
    def OnButtonEnd(self, event):
        self.Close()

    def OnButtonPrev(self, event):
        wx.PostEvent(self, PageChangeEvent(page=self.current_page.prev))
        
    def OnButtonNext(self, event):
        wx.PostEvent(self, PageChangeEvent(page=self.current_page.next))

class AeroPage(wx.Panel):
    def __init__(self, parent, title, data = None):
        wx.Panel.__init__(self, parent, -1, (-1, -1))
        self.title = title
        self.is_end = False
        self.items = []
        self.data = data
        self.next = None
        self.prev = None
        self.SetBackgroundColour("#ffffff")
        self._aero_layout()
        self.Show(False)
        
    def _aero_layout(self):
        margin = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(margin)
        margin.AddSpacer(38)
        self.content = self.makePageTitle(self.title)
        """
        self.content = wx.Panel(self)
        self.content.SetBackgroundColour("black")
        """
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
        self.items.append((item, proportion, flag, border))
    
    def GetNext(self):
        return self.next
    
    def GetPrev(self):
        return self.prev

    def GoToNext(self):
        if self.next:
            wx.PostEvent(self.Parent, PageChangeEvent(page=self.next))
    
    def GoToPrev(self):
        if self.prev:
            wx.PostEvent(self.Parent, PageChangeEvent(page=self.prev))


def AeroWizard_Chain(a, b):
    '''
    Encadenar las páginas
    '''
    a.next = b
    b.prev = a