import cv2
import datetime
import os
import pyttsx3
import threading
import queue

# 質問リスト
QUESTIONS = [
    "自己紹介を1分程度で簡潔にお願いします。",
    "あなたの最大の強みは何ですか？それをどう仕事に活かせると考えていますか？",
    "人生で一番辛かったこと、または挫折した経験と、そこからの学びを教えてください。",
    "弊社を志望した具体的な理由を教えてください。",
    "5年後、10年後のご自身のキャリアビジョンを教えてください。",
    "あなたが仕事において、これだけは譲れないという『美学』や『ポリシー』は何ですか？",
    "最後に、私（面接官）に対して、あなたを採用すべき最大の理由をぶつけてください。"
]

class InterviewMirror:
    def __init__(self):
        self.engine = pyttsx3.init()
        # 日本語音声の設定（環境によって異なる場合があります）
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "Japanese" in voice.name or "JP" in voice.id:
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 180)  # 読み上げスピード

        self.q_idx = 0
        self.is_speaking = False
        self.msg_queue = queue.Queue()

    def speak_worker(self):
        """別スレッドで音声を再生するワーカー"""
        while True:
            text = self.msg_queue.get()
            if text is None: break
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_speaking = False
            self.msg_queue.task_done()

    def start(self):
        # 音声スレッドの開始
        t = threading.Thread(target=self.speak_worker, daemon=True)
        t.start()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("エラー: カメラが見つかりません。")
            return

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = 20.0

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interview_practice_{timestamp}.avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

        print(f"--- AI面接官モード開始 ---")
        print(f"保存先: {filename}")
        print("操作: [n] 次の質問 / [q] 終了・保存")

        # 最初の質問を投下
        self.msg_queue.put(QUESTIONS[self.q_idx])

        while True:
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.flip(frame, 1) # 鏡表示

            # ステータス表示
            status_text = "INTERVIEWER SPEAKING..." if self.is_speaking else "WAITING FOR RESPONSE..."
            color = (0, 0, 255) if self.is_speaking else (0, 255, 0)
            cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            # 現在の質問（字幕風）
            current_q = f"Q{self.q_idx + 1}: {QUESTIONS[self.q_idx]}"
            cv2.putText(frame, current_q, (20, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            out.write(frame)
            cv2.imshow('AI Interviewer Mirror', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n'):
                if not self.is_speaking:
                    self.q_idx = (self.q_idx + 1) % len(QUESTIONS)
                    self.msg_queue.put(QUESTIONS[self.q_idx])

        self.msg_queue.put(None)
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"--- 練習終了 ---")

if __name__ == "__main__":
    mirror = InterviewMirror()
    mirror.start()
