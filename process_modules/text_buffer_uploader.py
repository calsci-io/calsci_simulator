from process_modules.uploader import BaseUploader
from ui import present
class TextUploader(BaseUploader):
    def __init__(self, disp_out, chrs, t_b, selection_provider=None):
        super().__init__(disp_out=disp_out, chrs=chrs)
        self.buffer_klass = t_b
        self.selection_provider = selection_provider


    def update(self, t_b_new):
        self.buffer_klass=t_b_new
    

    def refresh(self, state="default"):
        buf = self.buffer_klass.buffer()
        ref_ar = self.buffer_klass.ref_ar()
        start_row = ref_ar[0]//self.buffer_klass.cols
        end_row = ref_ar[1]//self.buffer_klass.cols
        selection = self.selection_provider() if self.selection_provider else None
        sel_start = selection[0] if selection else None
        sel_end = selection[1] if selection else None
        for i in range(start_row, end_row):
            self._clear_row_display(i)
            if buf[i].strip()!="" or self.buffer_klass.cursor()//self.buffer_klass.cols==i:
                j_counter=0
                for j in buf[i]:
                    idx = j_counter + i * self.buffer_klass.cols
                    invert = idx == self.buffer_klass.cursor()
                    if selection and sel_start <= idx < sel_end:
                        invert = True
                    self._print_character(j, invert=invert)
                    j_counter+=1
            else:
                self._print_character(" ", invert=False)

        self._display_bar(state)
        present()
