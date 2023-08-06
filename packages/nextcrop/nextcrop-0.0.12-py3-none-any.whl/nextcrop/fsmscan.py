from transitions import Machine


class FsmScan:
    def __init__(self, ui_scan):
        from nextcrop import UiScan  # only used for typing
        # TODO use dataclasses once python 3.7 is available
        self.ctrl: UiScan = ui_scan
        tr = 'trigger'
        src = 'source'
        dst = 'dest'
        states = ['initial', 'b0s0i0', 'b0s1i0', 'b0s0i1', 'b0s1i1', 'b1s0i1', 'b1s1i1', 'exit']
        transitions = [
            {tr: 'init',       src: 'initial', dst: 'b0s0i0'},
            {tr: 'scan',       src: 'b0s0i0',  dst: 'b0s1i0'},
            {tr: 'scan_done',  src: 'b0s1i0',  dst: 'b0s0i1'},
            {tr: 'scan',       src: 'b0s0i1',  dst: 'b0s1i1'},
            {tr: 'scan_done',  src: 'b0s1i1',  dst: 'b1s0i1'},
            {tr: 'scan',       src: 'b1s0i1',  dst: 'b1s1i1'},
            {tr: 'next',       src: 'b1s0i1',  dst: 'b0s0i1', 'before': 'save_cropped_images', 'conditions': 'last_image_in_buffer'},
            {tr: 'next',       src: 'b1s0i1',  dst: 'b1s0i1', 'before': 'save_and_next', 'unless': 'last_image_in_buffer'},
            {tr: 'scan',       src: 'b0s0i1',  dst: 'b1s1i1'},
            {tr: 'scan_done',  src: 'b1s1i1',  dst: 'b1s0i1'},
            {tr: 'next',       src: 'b0s0i1',  dst: 'exit'}
        ]
        self.fsm = Machine(model=self, states=states, transitions=transitions, initial='b0s0i0')

        import logging
        logging.basicConfig(level=logging.DEBUG)
        # Set transitions' log level to INFO; DEBUG messages will be omitted
        logging.getLogger('transitions').setLevel(logging.INFO)

    def on_enter_b0s0i0(self):
        self.ctrl.set_button_scan(True, 'Scan')
        self.ctrl.set_button_next(False, 'Next')

    def on_enter_b0s1i0(self):
        self.ctrl.set_button_scan(False, 'Scanning...')
        self.ctrl.set_button_next(False, 'Next')
        self.ctrl.scan()

    def on_enter_b0s0i1(self):
        self.ctrl.set_button_scan(True, 'Scan')
        self.ctrl.set_button_next(True, 'Save and exit')
        self.ctrl.next_image()
        self.ctrl.crop_and_show()

    def on_enter_b0s1i1(self):
        self.ctrl.scan()

    def on_enter_b1s0i1(self):
        self.ctrl.set_button_scan(True, 'Scan')
        self.ctrl.set_button_next(True, f'Save and next ({self.ctrl.scanner_buffer.image_count()} more)')

    def on_enter_b1s1i1(self):
        self.ctrl.set_button_scan(False, 'Scanning...')
        self.ctrl.set_button_next(True, f'Save and next ({self.ctrl.scanner_buffer.image_count()} more)')
        self.ctrl.scan()

    def on_enter_exit(self):
        self.ctrl.save_cropped_images()
        self.ctrl.exit()

    def save_cropped_images(self):
        self.ctrl.save_cropped_images()
        self.ctrl.crop_and_show()

    def save_and_next(self):
        self.ctrl.save_cropped_images()
        self.ctrl.next_image()
        self.ctrl.crop_and_show()

    def last_image_in_buffer(self):
        return self.ctrl.scanner_buffer.image_count() == 1
