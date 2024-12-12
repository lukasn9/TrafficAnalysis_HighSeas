import cv2

class LineEditor:
    def __init__(self, toggle_button):

            # Read the first frame


        self.start_point = None
        self.end_point = None
        self.lines = []
        self.names = []
        self.toggle_button = toggle_button

    def mouse_callback(self, x, y):
        if self.start_point is None:
            self.start_point = (x, y)
        elif self.start_point is not None and self.end_point is None:
            self.end_point = (x, y)
            self.lines.append((self.start_point, self.end_point))
            self.names.append("")
            self.draw_lines()
            self.start_point = None
            self.end_point = None

    def change_image(self, frame):
        self.original_image = frame
        self.image = self.original_image
        self.draw_lines()
    def all_set(self):
        return self.current_street >= len(self.ulice)
    def draw_lines(self):
        self.image = self.original_image.copy()

        for line in self.lines:
            cv2.line(self.image, line[0], line[1], (0, 255, 0), 2)
        if self.start_point is not None and self.end_point is not None:
            cv2.line(self.image, self.start_point, self.end_point, (0, 0, 255), 2)
    def reset_lines(self):
        self.lines = []
        self.toggle_button(False)



