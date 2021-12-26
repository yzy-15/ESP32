""" 按键事件模块 """
import utime
from machine import Pin, Timer

NOT_INIT = -1
TIMER_ID = -1
DOUBLE_CLICK_COUNT = 2
DOUBLE_CLICK_MAX_MS = 500
SHORT_PRESS_MS = 2000
LONG_PRESS_MS = 4000

class KeyEventID:
    """ 按键事件ID """
    KEY_PRESS = 0        # 按键按下
    KEY_RELEASE = 1      # 按键释放
    KEY_DOUBLE_CLICK = 2 # 双击 500ms内按下两次按键
    KEY_SHORT_PRESS = 3  # 短按 2s
    KEY_LONG_PRESS = 4   # 长按 4s

class Key():
    def __init__(self) -> None:
        self.__keyEventCallback = {
            KeyEventID.KEY_PRESS: None,
            KeyEventID.KEY_RELEASE: None,
            KeyEventID.KEY_DOUBLE_CLICK: None,
            KeyEventID.KEY_SHORT_PRESS: None,
            KeyEventID.KEY_LONG_PRESS: None,
        }
        self.__key = Pin(0,Pin.IN,Pin.PULL_UP)
        self.__key.irq(self.__KeyEvent, Pin.IRQ_FALLING)
        self.__lastKeyValue = NOT_INIT
        self.__KeyPressCount = 0
        self.__pressTime = 0
        self.__timer = Timer(TIMER_ID)
    def SetKeyEventCb(self, eventId: KeyEventID, eventCallback = None):
        self.__keyEventCallback[eventId] = eventCallback
    def __timeOutCb(self, timer = None):
        timeDiff = utime.ticks_ms() - self.__pressTime
        if timeDiff >= SHORT_PRESS_MS and timeDiff < LONG_PRESS_MS:
            # print("key short press, timeDiff:{}".format(timeDiff))
            if self.__keyEventCallback[KeyEventID.KEY_SHORT_PRESS] != None:
                self.__keyEventCallback[KeyEventID.KEY_SHORT_PRESS]()
        elif timeDiff >= LONG_PRESS_MS:
            # print("key long press, timeDiff:{}".format(timeDiff))
            if self.__keyEventCallback[KeyEventID.KEY_LONG_PRESS] != None:
                self.__keyEventCallback[KeyEventID.KEY_LONG_PRESS]()
            self.__timer.deinit()

    def __KeyEvent(self, key:Pin):
        """ 按键中断函数 """
        if self.__lastKeyValue == NOT_INIT:
            self.__lastKeyValue = key.value()
        elif self.__lastKeyValue != key.value():
            self.__lastKeyValue = key.value()
        else:
            return
        timeNow = utime.ticks_ms()
        timeDiff = 0
        if self.__pressTime != 0:
            timeDiff = timeNow - self.__pressTime
        if self.__KeyPressCount > DOUBLE_CLICK_COUNT or timeDiff >= DOUBLE_CLICK_MAX_MS:
            self.__pressTime = 0
            self.__KeyPressCount = 0
        if key.value() == KeyEventID.KEY_PRESS:
            self.__KeyPressCount += 1
            """ 打印的是距离上一次按下的时间 """
            # print("key press, timeDiff:{},PressCount:{}".format(timeDiff, self.__KeyPressCount))
            if self.__keyEventCallback[KeyEventID.KEY_PRESS] != None:
                self.__keyEventCallback[KeyEventID.KEY_PRESS]()
            if self.__pressTime == 0:
                """ 记录第一次按下的时间 """
                self.__pressTime = timeNow
            self.__timer.deinit()
            self.__timer.init(mode=Timer.PERIODIC, period = SHORT_PRESS_MS, callback = self.__timeOutCb)
        elif key.value() == KeyEventID.KEY_RELEASE:
            """ 打印的时按下到弹起的时间 """
            if self.__KeyPressCount == DOUBLE_CLICK_COUNT and timeDiff < DOUBLE_CLICK_MAX_MS:
                # print("key double click, timeDiff:{},PressCount:{}".format(timeDiff, self.__KeyPressCount))
                """ 双击事件 """
                if self.__keyEventCallback[KeyEventID.KEY_DOUBLE_CLICK] != None:
                    self.__keyEventCallback[KeyEventID.KEY_DOUBLE_CLICK]()
            # print("key release, timeDiff:{},PressCount:{}".format(timeDiff, self.__KeyPressCount))
            if self.__keyEventCallback[KeyEventID.KEY_RELEASE] != None:
                self.__keyEventCallback[KeyEventID.KEY_RELEASE]()
            self.__timer.deinit()
        else:
            pass

if __name__ == '__main__':
    """ 按键测试 """
    key = Key()
    key.SetKeyEventCb(KeyEventID.KEY_PRESS, lambda: print("key press"))
    key.SetKeyEventCb(KeyEventID.KEY_RELEASE, lambda: print("key release"))
    key.SetKeyEventCb(KeyEventID.KEY_DOUBLE_CLICK, lambda: print("key double click"))
    key.SetKeyEventCb(KeyEventID.KEY_SHORT_PRESS, lambda: print("key short press"))
    key.SetKeyEventCb(KeyEventID.KEY_LONG_PRESS, lambda: print("key long press"))
