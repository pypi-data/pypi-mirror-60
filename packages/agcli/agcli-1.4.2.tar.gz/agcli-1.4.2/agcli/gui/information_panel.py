import wx
from ..utils import terminal
from .component.custom_collapsible_pane import CustomCollapsiblePane

class InformationPanel(CustomCollapsiblePane):

    def __init__(self, parent, command_name):
        super().__init__(parent, label="Short help")
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.GetPane().SetSizer(sizer)
        info_message = self._get_info_message(command_name)
        static_text = wx.StaticText(self.GetPane(), label=info_message)
        sizer.Add(static_text, flag=wx.EXPAND|wx.ALL, border=5, proportion=1)
        self.Collapse(False)
        self.GetParent().Layout()
        self.GetParent().PostSizeEvent()

    def _get_info_message(self, cmd):
        """
        Retrieve the help message of the command and format it to take the summary
        part of the help. If the command doesn't support the "--help" option,
        only "cmd" is returned. 
        """
        return_code, out, err = terminal.to_cli("{} --help".format(cmd))
        if return_code == 0:
            info_message = out.split('\n\n')[0]
        else:
            info_message = cmd
        return info_message
