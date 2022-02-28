import win32com.client
from typing import Tuple


class Oscilloscope(object):

    def __init__(self) -> None:
        self.scope = win32com.client.Dispatch('LeCroy.XStreamDSO')
        self.c1 = self.scope.Acquisition.C1
        self.c2 = self.scope.Acquisition.C2

        # Default Scope Values
        self.time_scale = 1.0
        self.time_offset = 0.0
        self.c1_vertical_scale = 1.0
        self.c2_vertical_scale = 1.0
        self.samples = 20000
        self.sampling_rate = 1000000  # 1MHz
        self.trigger_channel = 1
        self.trigger_level = 1
        self.trigger_coupling = 'ac'
        self.trigger_slope = 'positive'
        self.trigger_mode = 'auto'

    def change_time_scale(self, horizontal_scale: float) -> str:
        try:
            self.scope.Acquisition.Horizontal.HorScale = horizontal_scale
            self.time_scale = self.scope.Acquisition.Horizontal.HorScale
            return f'[INFO][Time Scale]:{self.time_scale}'
        except Exception as e:
            print(e)
            return f'[ERROR]: Could not change time scale'

    def change_time_offset(self, horizontal_offset: float) -> str:
        try:
            self.scope.Acquisition.Horizontal.HorOffset = horizontal_offset
            self.time_offset = self.scope.Acquisition.Horizontal.HorOffset
            return f'[INFO][Horizontal Offset]:{self.time_offset}'
        except Exception as e:
            return '[ERROR]: Could not change time offset'

    def change_vertical_scale(self, channel: int, scale: float) -> str:
        try:
            if channel == 1:
                self.c1.VerScale = scale
                self.c1_vertical_scale = self.c1.VerScale
                return f'[INFO][C1 Vertical Scale]:{self.c1_vertical_scale}'
            elif channel == 2:
                self.c2.VerScale = scale
                self.c2_vertical_scale = self.c2.VerScale
                return f'[INFO][C1 Vertical Scale]:{self.c2_vertical_scale}'
            else:
                return f'[ERROR]: Invaild Channel Number'
        except Exception as e:
            return '[ERROR]: Could not change vertical scale'

    def change_samples_per_read(self, samples_per_read: int) -> str:
        try:
            self.c1.Out.Result.Samples = samples_per_read
            self.c2.Out.Result.Samples = samples_per_read
            self.samples = self.c1.Out.Result.Samples
            return f'[INFO][Samples]:{self.samples}'
        except Exception as e:
            return '[ERROR]: Could not change samples per read'

    def change_sampling_rate(self, sampling_rate: int) -> str:
        try:
            self.scope.Acquisition.Horizontal.SampleRate = sampling_rate
            self.sampling_rate = self.scope.Acquisition.Horizontal.SampleRate
            return f'[INFO]:{self.sampling_rate}'
        except Exception as e:
            return '[ERROR]: Could not change sampling rate'

    def auto_setup(self) -> str:
        try:
            self.scope.AutoSetup
            return "[INFO]:Auto Setup Done"
        except Exception as e:
            return('[ERROR] Could not do auto setup')

    def exit(self) -> str:
        try:
            self.scope.Exit
            return "[INFO]:Exit done"
        except Exception as e:
            return '[ERROR]: Could not exit'

    def change_trigger_source(self, trigger_channel: int) -> str:
        try:
            if trigger_channel == 1 or trigger_channel == 2:
                self.scope.Acquisition.Trigger.Edge.Source = f'C{trigger_channel}'
                self.trigger_channel = self.scope.Acquisition.Trigger.Edge.Source
                return f'[INFO][Trigger Source]:{self.scope.Acquisition.Trigger.Edge.Source}'
            else:
                return f'[ERROR]: Invaild Channel Number'
        except Exception as e:
            return '[ERROR]: Could not change trigger source'

    def change_trigger_level(self, trigger_level: float) -> str:
        try:
            self.scope.Acquisition.Trigger.Edge.Level = trigger_level
            self.trigger_level = self.scope.Acquisition.Trigger.Edge.Level
            return f"[INFO][Trigger Level]:{self.scope.Acquisition.Trigger.Edge.Level}"
        except Exception as e:
            return '[ERROR]: Could not change trigger level'

    def change_trigger_coupling(self, trigger_couple: str) -> str:
        try:
            if trigger_couple == 'ac' or trigger_couple == 'dc':
                trigger_couple = trigger_couple.upper()
                self.scope.Acquisition.Trigger.Edge.Coupling = trigger_couple
                self.trigger_coupling = self.scope.Acquisition.Trigger.Edge.Coupling
                return f'[INFO][Trigger Coupling]:{self.scope.Acquisition.Trigger.Edge.Coupling}'
            else:
                return f'[ERROR]: Invalid Coupling type'
        except Exception as e:
            return '[ERROR]: Could not change trigger coupling'

    def change_trigger_slope(self, trigger_slope: str) -> str:
        try:
            if trigger_slope == 'positive' or trigger_slope == 'negative' or trigger_slope == 'either':
                trigger_slope = trigger_slope.capitalize()
                self.scope.Acquisition.Trigger.Edge.Slope = trigger_slope
                self.trigger_slope = self.scope.Acquisition.Trigger.Edge.Slope
                return f'[INFO][Trigger Slope]:{self.scope.Acquisition.Trigger.Edge.Slope}'
            else:
                return f'[ERROR]: Invalid Slope type'
        except Exception as e:
            return '[ERROR]: Could not change trigger slope'

    def change_trigger_mode(self, trigger_mode: str) -> str:
        try:
            if trigger_mode == 'auto' or trigger_mode == 'single' or trigger_mode == 'normal' or trigger_mode == 'stopped':
                trigger_mode = trigger_mode.capitalize()
                self.scope.Acquisition.TriggerMode = trigger_mode
                self.trigger_mode = self.scope.Acquisition.TriggerMode
                return f'[INFO][Trigger Mode]:{self.scope.Acquisition.TriggerMode}'
            else:
                return f'[ERROR]: Invalid Trigger Mode'
        except Exception as e:
            return '[ERROR]: Could not change trigger mode'

    def read_once(self, channel: int) -> Tuple[int, Tuple]:
        self.scope.Acquisition.Horizontal.SampleRate = self.sampling_rate

        if channel == 1:
            self.c1.Out.Result.Samples = self.samples
            measurement = self.c1.Out.Result.DataArray
            return 1, measurement
        elif channel == 2:
            self.c2.Out.Result.Samples = self.samples
            measurement = self.c2.Out.Result.DataArray
            return 2, measurement

    def read_around_trigger(self) -> Tuple[Tuple, Tuple]:
        self.change_trigger_mode('single')

        is_triggered = self.scope.Acquisition.Acquire(10)

        if is_triggered == 1:
            ch1 = self.c1.Out.Result.DataArray
            ch2 = self.c2.Out.Result.DataArray
            self.change_trigger_mode('auto')
            return ch1, ch2
        else:
            print('timed out')
            return ((0), (0))


if __name__ == '__main__':
    scope = Oscilloscope()
    c1, c2 = scope.read_around_trigger()
    print(type(c1))
    scope.change_trigger_mode('auto')
    c1, c2 = scope.read_around_trigger()
    print(type(c1))
