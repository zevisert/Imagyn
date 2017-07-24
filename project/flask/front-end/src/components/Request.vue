<template>
  <div class="request">
    BefusedBequest
  </div>
</template>

<script>
/*
import _ from 'lodash'
import axios from 'axios'
*/
export default {
  name: 'search',
  data () {
    return {
      query: '',
      options: []
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.request {
  display: flex;
  justify-content: space-around;
}

h1 {
  font-size: 10em;
  margin-bottom: 20px;
  margin-top: 0;
}

.request-inner {
  text-align: center;
  margin-top: 100px;
}
</style>
