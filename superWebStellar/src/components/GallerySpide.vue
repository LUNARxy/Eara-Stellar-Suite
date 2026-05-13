<template>
  <div class="wrapper">

    <Splide
        :options="thumbsOptions"
        ref="thumbs"
    >
      <SplideSlide v-for="slide in slides" :key="slide.alt">
        <img :src="slide.src" :alt="slide.alt" loading="lazy">
      </SplideSlide>
    </Splide>

    <Splide
        :options="mainOptions"
        ref="main"
    >
      <SplideSlide v-for="slide in slides" :key="slide.alt" loading="lazy">
        <img :src="slide.src" :alt="slide.alt">
        <div class="splide_div_description">&nbsp;</div>
        <div class="splide_description">
          {{slide.alt}}
        </div>
      </SplideSlide>
    </Splide>
  </div>
</template>

<script lang="ts">
import { Splide, SplideSlide, Options } from '@splidejs/vue-splide';
import '@splidejs/splide/dist/css/splide.min.css';
import { defineComponent, onMounted, ref } from 'vue';
export default defineComponent( {
  name: 'GallerySpide',
  components: {
    Splide,
    SplideSlide,
  },
  props: {
    slides: Array,
  },
  setup() {
    const main   = ref<InstanceType<typeof Splide>>();
    const thumbs = ref<InstanceType<typeof Splide>>();
    const mainOptions: Options = {
      perPage: 1,
      perMove: 1,
      //gap: '1rem',
      pagination: false,
      height: 'auto'
    };
    const thumbsOptions: Options = {
      type: 'slide',
      rewind: false,
      gap: '1rem',
      pagination: false,
      fixedWidth: 110,
      fixedHeight: 70,
      cover: true,
      focus: 'center',
      isNavigation: true,
      updateOnMove: false,
      arrows: false // disbale arrows
    };
    onMounted( () => {
      const thumbsSplide = thumbs.value?.splide;
      if ( thumbsSplide ) {
        main.value?.sync( thumbsSplide );
      }
    } );
    return {
      main,
      thumbs,
      mainOptions,
      thumbsOptions,
    }
  },
});

</script>

<style>
.wrapper {
  max-width: 100%;
  margin: 0 auto;
}
.splide__slide img {
  width: 100%;
  height: auto;
}
.splide--nav {
  margin-bottom: 20px;
}
.splide__arrow--prev, .splide__arrow--next{
  top: 20%;
}
.splide_div_description{
  position: absolute;
  top: 0;
  left: 50%;
  transform: translate(-50%, 0%);
  width: 100%;
  background: #fff;
  opacity: 0.5;
  padding: 1.3rem;
  color: #000000;
}
.splide_description{
  position: absolute;
  top: 0;
  left: 50%;
  transform: translate(-50%, 0%);
  width: 100%;
  padding: 1rem;
  color: #000000;
}
.gallery-thumbnail > a > img{
  max-width: 100%;
}
</style>