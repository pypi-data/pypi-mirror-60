import random

import librosa
import numpy as np
from scipy.signal import butter, lfilter

from audiomentations.core.transforms_interface import BasicTransform
from audiomentations.core.utils import read_dir


class AddImpulseResponse(BasicTransform):
    """Convolve the audio with a random impulse response.
    Impulse responses can be created using http://tulrich.com/recording/ir_capture/
    Impulse responses are represented as a wav files in the given ir_path
    """

    def __init__(self, ir_path="/tmp/ir", p=0.5):
        """
        :param ir_path: Path to a folder that contains one or more wav files of impulse
        responses. No other files should reside in this folder. Must be str or a Path instance.
        :param p:
        """
        super().__init__(p)
        self.ir_files = read_dir(ir_path)

    def __apply_ir(self, input_signal, sr, ir_filename):
        ir, sr2 = librosa.load(ir_filename, sr)
        if sr != sr2:
            # This will typically not happen, as librosa should automatically resample the
            # impulse response sound to the desired sample rate
            raise Exception(
                "Recording sample rate {} did not match Impulse Response signal"
                " sample rate {}!".format(sr, sr2)
            )
        signal_ir = np.convolve(input_signal, ir)
        max_value = max(np.amax(signal_ir), -np.amin(signal_ir))
        scale = 0.5 / max_value
        signal_ir *= scale
        return signal_ir

    def apply(self, samples, sample_rate):
        ir_filename = random.choice(self.ir_files)
        samples = self.__apply_ir(samples, sample_rate, ir_filename)
        return samples


class FrequencyMask(BasicTransform):
    """Mask some frequency band on the spectrogram. Inspired by https://arxiv.org/pdf/1904.08779.pdf """

    def __init__(self, min_frequency_band=0.0, max_frequency_band=0.5, p=0.5):
        """
        :param min_frequency_band: Minimum bandwidth, float
        :param max_frequency_band: Maximum bandwidth, float
        :param p:
        """
        super().__init__(p)
        self.min_frequency_band = min_frequency_band
        self.max_frequency_band = max_frequency_band

    def __butter_bandstop(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype="bandstop")
        return b, a

    def __butter_bandstop_filter(self, data, lowcut, highcut, fs, order=5):
        b, a = self.__butter_bandstop(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data).astype(np.float32)
        return y

    def apply(self, samples, sample_rate):
        band_width = random.randint(
            self.min_frequency_band * sample_rate // 2,
            self.max_frequency_band * sample_rate // 2,
        )
        freq_start = random.randint(16, sample_rate / 2 - band_width)
        samples = self.__butter_bandstop_filter(
            samples, freq_start, freq_start + band_width, sample_rate, order=6
        )
        return samples


class TimeMask(BasicTransform):
    """Mask some time band on the spectrogram. Inspired by https://arxiv.org/pdf/1904.08779.pdf """

    def __init__(self, min_band_part=0.0, max_band_part=0.5, fade=False, p=0.5):
        """
        :param min_band_part: Minimum length of the silent part as a fraction of the
            total sound length. Float.
        :param max_band_part: Maximum length of the silent part as a fraction of the
            total sound length. Float.
        :param fade: Bool, Add linear fade in and fade out of the silent part.
        :param p:
        """
        super().__init__(p)
        self.min_band_part = min_band_part
        self.max_band_part = max_band_part
        self.fade = fade

    def apply(self, samples, sample_rate):
        new_samples = samples.copy()
        _t = random.randint(
            int(new_samples.shape[0] * self.min_band_part),
            int(new_samples.shape[0] * self.max_band_part),
        )
        _t0 = random.randint(0, new_samples.shape[0] - _t)
        mask = np.zeros(_t)
        if self.fade:
            fade_length = min(int(sample_rate * 0.01), int(_t * 0.1))
            mask[0:fade_length] = np.linspace(1, 0, num=fade_length)
            mask[-fade_length:] = np.linspace(0, 1, num=fade_length)
        new_samples[_t0 : _t0 + _t] *= mask
        return new_samples


class AddGaussianSNR(BasicTransform):
    """Add gaussian noise to the samples with random Signal to Noise Ratio (SNR) """

    def __init__(self, min_SNR=0.001, max_SNR=1.0, p=0.5):
        """

        :param min_SNR: Minimum signal-to-noise ratio
        :param max_SNR: Maximum signal-to-noise ratio
        :param p:
        """
        super().__init__(p)
        self.min_SNR = min_SNR
        self.max_SNR = max_SNR

    def apply(self, samples, sample_rate):
        mean, std = np.mean(samples), np.std(samples)
        noise_std = random.uniform(self.min_SNR * std, self.max_SNR * std)
        noise = np.random.normal(mean, noise_std, size=len(samples)).astype(np.float32)
        return samples + noise


class AddGaussianNoise(BasicTransform):
    """Add gaussian noise to the samples"""

    def __init__(self, min_amplitude=0.001, max_amplitude=0.015, p=0.5):
        super().__init__(p)
        self.min_amplitude = min_amplitude
        self.max_amplitude = max_amplitude

    def apply(self, samples, sample_rate):
        noise = np.random.randn(len(samples)).astype(np.float32)
        amplitude = random.uniform(self.min_amplitude, self.max_amplitude)
        samples = samples + amplitude * noise
        return samples


class TimeStretch(BasicTransform):
    """Time stretch the signal without changing the pitch"""

    def __init__(self, min_rate=0.8, max_rate=1.25, leave_length_unchanged=True, p=0.5):
        super().__init__(p)
        assert min_rate > 0.1
        assert max_rate < 10
        assert min_rate <= max_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.leave_length_unchanged = leave_length_unchanged

    def apply(self, samples, sample_rate):
        """
        If `rate > 1`, then the signal is sped up.
        If `rate < 1`, then the signal is slowed down.
        """
        rate = random.uniform(self.min_rate, self.max_rate)
        time_stretched_samples = librosa.effects.time_stretch(samples, rate)
        if self.leave_length_unchanged:
            # Apply zero padding if the time stretched audio is not long enough to fill the
            # whole space, or crop the time stretched audio if it ended up too long.
            padded_samples = np.zeros(shape=samples.shape, dtype=samples.dtype)
            window = time_stretched_samples[: samples.shape[0]]
            actual_window_length = len(window)  # may be smaller than samples.shape[0]
            padded_samples[:actual_window_length] = window
            time_stretched_samples = padded_samples
        return time_stretched_samples


class PitchShift(BasicTransform):
    """Pitch shift the sound up or down without changing the tempo"""

    def __init__(self, min_semitones=-4, max_semitones=4, p=0.5):
        super().__init__(p)
        assert min_semitones >= -12
        assert max_semitones <= 12
        assert min_semitones <= max_semitones
        self.min_semitones = min_semitones
        self.max_semitones = max_semitones

    def apply(self, samples, sample_rate):
        num_semitones = random.uniform(self.min_semitones, self.max_semitones)
        pitch_shifted_samples = librosa.effects.pitch_shift(
            samples, sample_rate, n_steps=num_semitones
        )
        return pitch_shifted_samples


class Shift(BasicTransform):
    """
    Shift the samples forwards or backwards. Samples that roll beyond the first or last position
    are re-introduced at the last or first.
    """

    def __init__(self, min_fraction=-0.5, max_fraction=0.5, p=0.5):
        """
        :param min_fraction: float, fraction of total sound length
        :param max_fraction: float, fraction of total sound length
        :param p:
        """
        super().__init__(p)
        assert min_fraction >= -1
        assert max_fraction <= 1
        self.min_fraction = min_fraction
        self.max_fraction = max_fraction

    def apply(self, samples, sample_rate):
        num_places_to_shift = int(
            round(random.uniform(self.min_fraction, self.max_fraction) * len(samples))
        )
        shifted_samples = np.roll(samples, num_places_to_shift)
        return shifted_samples


class Normalize(BasicTransform):
    """
    Apply a constant amount of gain, so that highest signal level present in the sound becomes
    0 dBFS, i.e. the loudest level allowed if all samples must be between -1 and 1. Also known
    as peak normalization.
    """

    def __init__(self, p=0.5):
        super().__init__(p)

    def apply(self, samples, sample_rate):
        max_amplitude = np.amax(np.abs(samples))
        normalized_samples = samples / max_amplitude
        return normalized_samples


class Trim(BasicTransform):
    """
    Trim leading and trailing silence from an audio signal using librosa.effects.trim
    """

    def __init__(self, top_db=20, p=1.0):
        super().__init__(p)
        self.top_db = top_db

    def apply(self, samples, sample_rate):
        samples, lens = librosa.effects.trim(samples, top_db=self.top_db)
        return samples


class Resample(BasicTransform):
    """
    Resample signal using librosa.core.resample

    To do downsampling only set both minimum and maximum sampling rate lower than original
    sampling rate and vice versa to do upsampling only.
    """

    def __init__(self, min_sample_rate=8000, max_sample_rate=44100, p=0.5):
        """
        :param min_sample_rate: int, Minimum sample rate
        :param max_sample_rate: int, Maximum sample rate
        :param p:
        """
        super().__init__(p)
        assert min_sample_rate <= max_sample_rate
        self.min_sample_rate = min_sample_rate
        self.max_sample_rate = max_sample_rate

    def apply(self, samples, sample_rate):
        target_sample_rate = random.randint(self.min_sample_rate, self.max_sample_rate)

        samples = librosa.core.resample(
            samples, orig_sr=sample_rate, target_sr=target_sample_rate
        )
        return samples


class ClippingDistortion(BasicTransform):
    """Distort signal by clipping a random percentage of points

    The percentage of points that will ble clipped is drawn from a uniform distribution between
    the two input parameters min_percentile_threshold and max_percentile_threshold. If for instance
    30% is drawn, the samples are clipped if they're below the 15th or above the 85th percentile.
    """

    def __init__(self, min_percentile_threshold=0, max_percentile_threshold=40, p=0.5):
        """
        :param min_percentile_threshold: int, A lower bound on the total percent of samples that will be clipped
        :param max_percentile_threshold: int, A upper bound on the total percent of samples that will be clipped
        :param p:
        """
        super().__init__(p)
        assert min_percentile_threshold <= max_percentile_threshold
        assert 0 <= min_percentile_threshold <= 100
        assert 0 <= max_percentile_threshold <= 100
        self.min_percentile_threshold = max_percentile_threshold
        self.max_percentile_threshold = max_percentile_threshold

    def apply(self, samples, sample_rate):
        percentile_threshold = random.randint(
            self.min_percentile_threshold, self.max_percentile_threshold
        )
        lower_percentile_threshold = int(percentile_threshold / 2)
        lower_threshold, upper_threshold = np.percentile(
            samples, [lower_percentile_threshold, 100 - lower_percentile_threshold]
        )
        samples = np.clip(samples, lower_threshold, upper_threshold)
        return samples
