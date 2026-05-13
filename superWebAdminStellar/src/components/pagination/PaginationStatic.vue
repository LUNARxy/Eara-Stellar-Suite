<template>
  <div>
    <!-- <div class="search">
      <input type="text" v-model="searchQuery" placeholder="Buscar..." />
    </div> -->
    <div>
      <slot :items="paginatedItems"></slot>
    </div>
    <div class="pagination mt-3">
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
        Anterior
      </button>
      <span v-for="page in visiblePages" :key="page">
        <template v-if="page === currentPage">
          <button class="btn-secondary right" type="button" @click="goToPage(page)">
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
        Siguiente
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
    items: {
      type: Array,
      required: true,
    },
    perPage: {
      type: Number,
      default: 10,
    },
  },
  data() {
    return {
      currentPage: 1,
      searchQuery: "",
    };
  },
  computed: {
    filteredItems() {
      return this.items.filter((item) =>
        Object.values(item).some((value) =>
          String(value).toLowerCase().includes(this.searchQuery.toLowerCase())
        )
      );
    },
    totalPages() {
      return Math.ceil(this.filteredItems.length / this.perPage);
    },
    paginatedItems() {
      const startIndex = (this.currentPage - 1) * this.perPage;
      return this.filteredItems.slice(startIndex, startIndex + this.perPage);
    },
    visiblePages() {
      const range = [];
      const start = Math.max(1, this.currentPage - 2);
      const end = Math.min(this.totalPages, this.currentPage + 2);

      for (let i = start; i <= end; i++) {
        range.push(i);
      }

      // Ajustar el rango para asegurar que siempre haya 5 botones cuando sea posible
      while (range.length < 5 && range[0] > 1) {
        range.unshift(range[0] - 1);
      }
      while (range.length < 5 && range[range.length - 1] < this.totalPages) {
        range.push(range[range.length - 1] + 1);
      }

      return range;
    },
    
  },
  methods: {
    goToPage(page) {
      this.currentPage = page;
    },
    nextPage() {
      this.currentPage++;
    },
    previousPage() {
      this.currentPage--;
    },
    goToFirstPage() {
      this.currentPage = 1;
    },
    goToLastPage() {
      this.currentPage = this.totalPages;
    },
  },
  watch: {
    searchQuery() {
      this.currentPage = 1; // Reset to first page on search
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

.pagination button.active {
  background-color: #4caf50;
  color: white;
}
</style>
