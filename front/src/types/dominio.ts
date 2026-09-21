export type LoginProviderStatus = 'password' | 'google' | 'password-and-google';
export type TechnicalProfileStatus = 'not-configured' | 'partially-configured' | 'configured' | 'requires-attention';
export type ProviderStatus = 'available' | 'unavailable' | 'deprecated';
export type TokenStatus = 'not-configured' | 'configured' | 'invalid' | 'requires-attention';

export interface UserProfile {
  mail: string;
  age: number;
  profession: string;
  displayName?: string | null;
  loginProviderStatus: LoginProviderStatus;
  technicalProfileStatus: TechnicalProfileStatus;
}

export interface AuthSessionResponse {
  user: UserProfile;
  accessToken: string;
  expiresInSeconds: number;
}

export interface ProviderTokenStatus {
  providerId: string;
  status: TokenStatus;
  maskedTokenLabel?: string | null;
  lastValidatedAt?: string | null;
}

export interface AIModel {
  modelId: string;
  displayName: string;
  availabilityStatus: ProviderStatus;
  capabilities: string[];
}

export interface ProviderWithModels {
  providerId: string;
  name: string;
  status: ProviderStatus;
  tokenStatus: ProviderTokenStatus;
  models: AIModel[];
}
