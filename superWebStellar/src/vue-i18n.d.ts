import 'vue-i18n';

declare module 'vue-i18n' {
  export interface DefineLocaleMessage {
    [key: string]: string;
  }

  export interface DefineDateTimeFormat {
    [key: string]: Intl.DateTimeFormatOptions;
  }

  export interface DefineNumberFormat {
    [key: string]: Intl.NumberFormatOptions;
  }
}

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $t: typeof import('vue-i18n').t;
  }
}