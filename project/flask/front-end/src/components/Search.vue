<template>
  <div class="search">
    <div class="search-inner">
      <h1>Imagyn</h1>
      <input type="text" placeholder="Search" v-model="query">
      <ul id="suggestion-list" v-if="options.length">
        <template v-for="(option, index) in options">
          <li :id="'suggestion-'+index" @click="selectOption(index)">
            {{option}}
          </li>
        </template>
      </ul>
    </div>
  </div>
</template>

<script>
import _ from 'lodash'
import axios from 'axios'
export default {
  name: 'search',
  data () {
    return {
      query: '',
      options: []
    }
  },
  watch: {
    query: function () {
      this.getOptions()
    }
  },
  methods: {
    getOptions: _.debounce(
      function () {
        if (this.query.length > 0) {
          axios.get('http://localhost:5000/api/suggestions/' + this.query)
            .then((response) => {
              this.options = response.data
            })
        } else {
          this.options = []
        }
      },
      500
    ),
    selectOption: function (index) {
      console.log(this.options[index])
      this.submitSearch(this.options[index])
    },
    submitSearch: function (searchQuery) {
      this.$router.push('/cloud/' + searchQuery)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.search {
  display: flex;
  justify-content: space-around;
}

h1 {
  font-size: 10em;
  margin-bottom: 20px;
  margin-top: 0;
}

.search-inner {
  text-align: center;
  margin-top: 100px;
}

input {
  position: relative;
  z-index: 1;
  color: #2c3e50;
  border: 0;
  box-shadow: 3px 3px 20px grey;
  padding-left: 20px;
  font-size: 6em;
}
input:focus {
  outline-width: 0;
}

#suggestion-list {
  margin: 0;
  padding: 0;
  position: relative;
  z-index: 2;
  background: white;
  box-shadow: 3px 3px 20px grey;
  list-style: none;
  text-align: left;
  display: flex;
  flex-direction: column;
}

#suggestion-list > li {
  font-size: 2.6em;
  padding: 3px 0px 3px 20px;
  border-bottom: 2px solid #CCC;
}

#suggestion-list > li:hover {
  background: #CCC;
  cursor: pointer;
}
</style>
