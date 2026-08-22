import numpy as np
import pandas as pd

from lib.time_series.base import ForecastModel, ModelMetadata


class LocalLevelParticleFilterModel(ForecastModel):
    """Bootstrap particle filter for a local-level log-price model.

    State equation:       x[t] = x[t-1] + state_noise
    Observation equation: log(price[t]) = x[t] + observation_noise

    This is an application extension and not a reproduction of a particular
    paper. Noise scales are estimated from the in-sample log-price changes.
    """

    metadata = ModelMetadata(
        key="particle_filter_local_level",
        name="粒子フィルタ（ローカルレベル）",
        description=(
            "潜在的な対数価格がランダムウォークに従うと仮定し、"
            "多数の粒子で状態分布を逐次推定する基本モデルです。"
        ),
        assumptions=(
            "潜在対数価格はランダムウォークに従う",
            "状態ノイズと観測ノイズは独立な正規分布に従う",
            "学習期間から推定したノイズ水準が予測期間も継続する",
        ),
        reference="Bootstrap particle filter / local-level state-space model",
    )
    minimum_observations = 30

    def __init__(
        self,
        particle_count: int = 1_000,
        state_noise_scale: float = 0.7,
        observation_noise_scale: float = 0.5,
        resample_threshold: float = 0.5,
        random_seed: int = 42,
    ) -> None:
        if particle_count < 100:
            raise ValueError("粒子数は100以上で指定してください。")
        if state_noise_scale <= 0 or observation_noise_scale <= 0:
            raise ValueError("ノイズ倍率は0より大きい値で指定してください。")
        if not 0 < resample_threshold <= 1:
            raise ValueError("リサンプリング閾値は0より大きく1以下で指定してください。")

        self.particle_count = particle_count
        self.state_noise_scale = state_noise_scale
        self.observation_noise_scale = observation_noise_scale
        self.resample_threshold = resample_threshold
        self.random_seed = random_seed

    def forecast(self, train: pd.Series, horizon: int) -> pd.Series:
        prices = self.validate(train, horizon)
        if (prices <= 0).any():
            raise ValueError("対数価格を扱うため、価格はすべて0より大きい必要があります。")

        log_prices = np.log(prices.to_numpy(dtype=float))
        empirical_scale = float(np.std(np.diff(log_prices), ddof=1))
        base_scale = max(empirical_scale, 1e-6)
        state_sigma = base_scale * self.state_noise_scale
        observation_sigma = base_scale * self.observation_noise_scale

        rng = np.random.default_rng(self.random_seed)
        particles = rng.normal(log_prices[0], observation_sigma, self.particle_count)
        weights = np.full(self.particle_count, 1.0 / self.particle_count)

        for observation in log_prices[1:]:
            particles += rng.normal(0.0, state_sigma, self.particle_count)
            weights = self._normalized_likelihood(
                observation, particles, observation_sigma
            )

            effective_sample_size = 1.0 / np.sum(weights**2)
            if effective_sample_size < self.resample_threshold * self.particle_count:
                indexes = self._systematic_resample(weights, rng)
                particles = particles[indexes]
                weights.fill(1.0 / self.particle_count)

        # Preserve the final filtering weights before simulating future states.
        indexes = self._systematic_resample(weights, rng)
        particles = particles[indexes]

        forecasts: list[float] = []
        for _ in range(horizon):
            particles += rng.normal(0.0, state_sigma, self.particle_count)
            forecasts.append(float(np.mean(np.exp(particles))))

        return pd.Series(forecasts, dtype=float)

    def _normalized_likelihood(
        self,
        observation: float,
        particles: np.ndarray,
        observation_sigma: float,
    ) -> np.ndarray:
        standardized_errors = (observation - particles) / observation_sigma
        log_weights = -0.5 * standardized_errors**2
        log_weights -= np.max(log_weights)
        weights = np.exp(log_weights)
        weight_sum = weights.sum()
        if not np.isfinite(weight_sum) or weight_sum == 0:
            return np.full(self.particle_count, 1.0 / self.particle_count)
        return weights / weight_sum

    def _systematic_resample(
        self, weights: np.ndarray, rng: np.random.Generator
    ) -> np.ndarray:
        positions = (rng.random() + np.arange(self.particle_count)) / self.particle_count
        cumulative_sum = np.cumsum(weights)
        cumulative_sum[-1] = 1.0
        return np.searchsorted(cumulative_sum, positions)
