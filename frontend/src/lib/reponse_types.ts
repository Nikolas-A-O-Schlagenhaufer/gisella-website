export interface BaseErrorReponseData {
  detail: string;
}
export interface Error401ResponseData extends BaseErrorReponseData {}

export interface TokenReponse {
  access_token: string;
  token_type: string;
  max_age: number;
}
