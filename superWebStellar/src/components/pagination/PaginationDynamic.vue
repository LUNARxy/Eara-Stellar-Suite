<template>
  <div>
    <div>
      <slot :items="items"></slot>
    </div>
    <div class="text-right pt-3">Total: {{totalItems}}</div>
    <div v-if="totalPages > 1" class="pagination mt-3">
      <button
          class="btn-primary right"
          @click="goToFirstPage"
          :disabled="currentPage === 1"
      >
        <i class="material-icons">first_page</i>
      </button>
      <button
          class="btn-primary right"
          type="button"
          @click="previousPage"
          :disabled="currentPage === 1"
      >
        {{ $t('views.Anterior') }}
      </button>
      <span v-for="page in visiblePages" :key="page">
        <template v-if="page === currentPage">
          <button class="btn-secondary right pagination_button_active" type="button" @click="goToPage(page)">
            {{ page }}
          </button>
        </template>
        <template v-else>
          <button class="btn-primary right" type="button" @click="goToPage(page)">
            {{ page }}
          </button>
        </template>
      </span>
      <button
          class="btn-primary right"
          type="button"
          @click="nextPage"
          :disabled="currentPage === totalPages"
      >
        {{ $t('views.Siguiente') }}
      </button>
      <button
          class="btn-primary right"
          @click="goToLastPage"
          :disabled="currentPage === totalPages"
      >
        <i class="material-icons">last_page</i>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    serviceFunction: {
      type: String,
      required: true,
    },
    functionParams: {
      type: Object,
      required: true,
    },
    perPage: {
      type: Number,
      default: 10,
    },
  },
  data() {
    return {
      items: [],
      currentPage: 1,
      totalItems: 0,
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalItems / this.perPage);
    },
    visiblePages() {
      let total_buttons = 3
      let total_buttons_back_prev = 1

      const range = [];
      const start = Math.max(1, this.currentPage - total_buttons_back_prev);
      const end = Math.min(this.totalPages, this.currentPage + total_buttons_back_prev);

      for (let i = start; i <= end; i++) {
        range.push(i);
      }

      // Ajustar el rango para asegurar que siempre haya 3 botones cuando sea posible
      while (range.length < total_buttons && range[0] > 1) {
        range.unshift(range[0] - 1);
      }
      while (range.length < total_buttons && range[range.length - 1] < this.totalPages) {
        range.push(range[range.length - 1] + 1);
      }

      return range;
    }
  },
  methods: {
    async fetchData() {
      const params = {
        ...this.functionParams,
        page: this.currentPage,
        perPage: this.perPage,
      };
      const data = await this.serviceFunction(params);
      this.items = data.data.list;
      this.totalItems = data.data.total;
      this.$emit('update-items', this.items)
    },
    goToPage(page) {
      this.currentPage = page;
      this.fetchData();
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.fetchData();
      }
    },
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.fetchData();
      }
    },
    goToFirstPage() {
      this.currentPage = 1;
      this.fetchData();
    },
    goToLastPage() {
      this.currentPage = this.totalPages;
      this.fetchData();
    },
  },
  created() {
    this.fetchData();
  },
  watch: {
    functionParams: {
      handler() {
        this.fetchData();
      },
      deep: true,
    },
  },
};
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
}

.pagination button {
  margin: 0 5px;
}

.pagination_button_active {
  opacity: 0.6;
}
</style>
