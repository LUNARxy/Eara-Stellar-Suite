import 'vue-router';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $route: ReturnType<typeof useRoute>;
    $router: ReturnType<typeof useRouter>;
  }
}