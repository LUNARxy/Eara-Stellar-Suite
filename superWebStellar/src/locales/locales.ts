import es from './../locales/es.json';
import en from './../locales/en.json';

export enum Locales {
    EN = 'en',
    ES = 'es',
}

export const messages = {
    [Locales.ES]: es,
    [Locales.EN]: en,
};
