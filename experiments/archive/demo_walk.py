from src.data_providers.real.spot_agent import SpotAgent
import time

def main():
    spot = SpotAgent()
    spot.move_vision_frame((-5.1, -8.4))
    spot.move_vision_frame((-5.1, -18.4))
    spot.move_vision_frame((-5.1, -23.4))

def reset():
    spot = SpotAgent()
    spot.move_vision_frame((0.0, 0.0))
    time.sleep(10)

def main2():
    spot = SpotAgent()

    spot.move_vision_frame((7.5, 0.0))
    time.sleep(15)
    spot.move_vision_frame((7.5, 11))
    time.sleep(15)
    spot.move_vision_frame((7.5, 16))
    time.sleep(15)
    spot.move_vision_frame((7.5, 11))
    time.sleep(15)
    spot.move_vision_frame((7.5, 0))
    time.sleep(15)
    spot.move_vision_frame((0.0, 0.0))
    time.sleep(15)

def with_fiducial():
    spot = SpotAgent()

    # spot.move_vision_frame((1, 0,0))
    time.sleep(15)
    spot.move_vision_frame((1, 7.5))
    time.sleep(15)
    spot.move_vision_frame((-10, 7.5))
    time.sleep(15)
    spot.move_vision_frame((-16, 11))
    time.sleep(15)
    spot.move_vision_frame((7.5, 0))
    time.sleep(15)
    spot.move_vision_frame((0.0, 0.0))
    time.sleep(15)


if __name__ == '__main__':
    main2()
