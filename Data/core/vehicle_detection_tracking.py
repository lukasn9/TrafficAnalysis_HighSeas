import numpy as np
import datetime
import cv2
from ultralytics import YOLO
from collections import deque

from ..deep_sort.deep_sort.tracker import Tracker
from ..deep_sort.deep_sort import nn_matching
from ..deep_sort.deep_sort.detection import Detection
from ..deep_sort.tools import generate_detections as gdet

from ..core.helper import create_video_writer

class TrafficAnalysis:
    def __init__(self, video_path, output_path, lines, streets, fast):
        self.current_frame = None
        self.frame = None
        self.video_path = video_path
        self.conf_threshold = 0.5
        self.max_cosine_distance = 0.4
        self.nn_budget = None
        self.variables_count = [0] * len(lines)
        self.variables_accumulator = [0] * len(lines)

        self.lines = lines
        self.points = [deque(maxlen=32) for _ in range(1000)]  # list of deques to store the points

        self.video_cap = cv2.VideoCapture(self.video_path)
        self.video_fps = self.video_cap.get(cv2.CAP_PROP_FPS)
        self.detectable_obj = ["car", "bus", "truck"]
        print(output_path)
        self.writer = create_video_writer(self.video_cap, output_path)
        self.model = YOLO("Data/models/yolov8n.pt" if fast else "Data/models/yolov8s.pt")
        self.model_filename = "Data/config/mars-small128.pb"
        self.encoder = gdet.create_box_encoder(self.model_filename, batch_size=1)
        self.metric = nn_matching.NearestNeighborDistanceMetric(
            "cosine", self.max_cosine_distance, self.nn_budget)
        self.tracker = Tracker(self.metric, max_age=50)
        self.classes_path = "Data/config/coco.names"
        self.vehicle_path = dict()
        self.vehicle_accumulator = []
        self.streets = streets
        self.added_objects = []
        with open(self.classes_path, "r") as f:
            self.class_names = f.read().strip().split("\n")
        np.random.seed(31)  # to get the same colors
        self.colors = np.random.randint(0, 255, size=(len(self.class_names), 3))  # (80, 3)

    def is_point_on_line(self, center_x, center_y, last_point_x, last_point_y, start_line, end_line):
        if start_line[0] == end_line[0]:
            return center_x > end_line[0] and min(start_line[1], end_line[1]) < center_y < max(start_line[1], end_line[1]) and last_point_x < end_line[0]
        elif start_line[1] == end_line[1]:
            return center_y > end_line[1] and min(start_line[0], end_line[0]) < center_x < max(start_line[0], end_line[0]) and last_point_y < end_line[1]
        else:
            m = (end_line[1] - start_line[1]) / (end_line[0] - start_line[0])
            c = start_line[1] - m * start_line[0]
            if abs(m) >= 1:
                x = (center_y - c) / m
                return (((center_x > x > last_point_x) or (center_x < x < last_point_x)) and min(start_line[1], end_line[1]) < center_y < max(start_line[1], end_line[1]))
            else:
                y = m * center_x + c
                return ((center_y > y > last_point_y) or (center_y < y < last_point_y)) and min(start_line[0], end_line[0]) < center_x < max(start_line[0], end_line[0])

    def update_scan_frame(self, current_time):
        start = datetime.datetime.now()
        ret, self.frame = self.video_cap.read()
        if not ret:
            print("End of the video file...")
            return True
        overlay = self.frame.copy()
        for line in self.lines:
            cv2.line(self.frame, line[0], line[1], (0, 255, 0), 5)
        frame = cv2.addWeighted(overlay, 0.5, self.frame, 0.5, 0)
        results = self.model(frame)
        for result in results:
            bboxes = []
            confidences = []
            class_ids = []
            for data in result.boxes.data.tolist():
                x1, y1, x2, y2, confidence, class_id = data
                x = int(x1)
                y = int(y1)
                w = int(x2) - int(x1)
                h = int(y2) - int(y1)
                class_id = int(class_id)

                if confidence > self.conf_threshold:
                    bboxes.append([x, y, w, h])
                    confidences.append(confidence)
                    class_ids.append(class_id)

        names = [self.class_names[class_id] for class_id in class_ids]
        features = self.encoder(frame, bboxes)

        dets = []
        for bbox, conf, class_name, feature in zip(bboxes, confidences, names, features):
            dets.append(Detection(bbox, conf, class_name, feature))

        self.tracker.predict()
        self.tracker.update(dets)

        for track in self.tracker.tracks:
            track_id = track.track_id
            class_name = track.get_class()

            if not track.is_confirmed() or track.time_since_update > 1:
                if class_name in self.detectable_obj and track_id in self.vehicle_path and track_id not in self.added_objects:
                    self.added_objects.append(track_id)

                    if len(self.vehicle_path[track_id]) > 1 and self.vehicle_path[track_id][0] != self.vehicle_path[track_id][-1]:
                        self.vehicle_accumulator.append({'from': self.streets[self.vehicle_path[track_id][0]], 'to': self.streets[self.vehicle_path[track_id][-1]], 'type': class_name, 'time': current_time.isoformat()})
                    else:
                        self.vehicle_accumulator.append({'from': self.streets[self.vehicle_path[track_id][0]], 'to': None, 'type': class_name, 'time': current_time.isoformat()})


                continue

            bbox = track.to_tlbr()
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

            class_id = self.class_names.index(class_name)
            color = self.colors[class_id]
            B, G, R = int(color[0]), int(color[1]), int(color[2])

            text = str(track_id) + " - " + class_name
            cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 3)
            cv2.rectangle(frame, (x1 - 1, y1 - 20), (x1 + len(text) * 12, y1), (B, G, R), -1)
            cv2.putText(frame, text, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            self.points[track_id].append((center_x, center_y))

            cv2.circle(frame, (center_x, center_y), 4, (0, 255, 0), -1)

            for i in range(1, len(self.points[track_id])):
                point1 = self.points[track_id][i - 1]
                point2 = self.points[track_id][i]
                if point1 is None or point2 is None:
                    continue

                cv2.line(frame, (point1), (point2), (0, 255, 0), 2)

            last_point_x = self.points[track_id][0][0]
            last_point_y = self.points[track_id][0][1]
            cv2.circle(frame, (int(last_point_x), int(last_point_y)), 4, (255, 0, 255), -1)
            for i in range(len(self.lines)):
                if self.is_point_on_line(center_x, center_y, last_point_x, last_point_y, self.lines[i][0],
                                         self.lines[i][1]):
                    if class_name in self.detectable_obj:
                        if track_id not in self.vehicle_path:
                            self.variables_accumulator[i] += 1
                            self.variables_count[i] += 1
                            self.vehicle_path[track_id] = [i]
                        elif self.vehicle_path[track_id][-1] != i:
                            self.variables_accumulator[i] += 1
                            self.variables_count[i] += 1
                            self.vehicle_path[track_id].append(i)




                    self.points[track_id].clear()



        end = datetime.datetime.now()
        fps = f"FPS: {1 / (end - start).total_seconds():.2f}"
        cv2.putText(frame, fps, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8)
        for i in range(len(self.lines)):
            cv2.putText(frame, self.streets[i], (int((self.lines[i][0][0] + self.lines[i][1][0]) / 2), int((self.lines[i][0][1] + self.lines[i][1][1]) / 2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            cv2.putText(frame, f"{self.variables_count[i]}", (int((self.lines[i][0][0] + self.lines[i][1][0]) / 2), int((self.lines[i][0][1] + self.lines[i][1][1]) / 2) + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2)

        #cv2.imshow("Frame", frame)
        self.current_frame = frame
        self.writer.write(self.current_frame)
        if cv2.waitKey(1) == ord("q"):
            return True

    def get_accumulated_values(self):
        accumulated_values = self.vehicle_accumulator
        self.vehicle_accumulator = []
        return accumulated_values

    def release_resources(self):
        self.video_cap.release()
        self.writer.release()
        cv2.destroyAllWindows()