<template>
  <div class="request">
    <div id="cloud-img-wrapper">
      <img id="cloud-img" src="../assets/cloud.png">
      <template v-if="!errored">
      <template v-if="download_complete">
        <h3>
          <i-count-up :start="0" :end="num_images" :duration="3.5"></i-count-up> images retrieved from <span class="bold-italics">the cloud</span>.
        </h3>
      </template>
      <template v-else>
        <h3>
          downloading images from <span class="bold-italics">the cloud</span><span class="dots">{{ dots }}</span>
        </h3>
      </template>
      </template>
      <template v-else>
        <h3>
          Download Error!
        </h3>
      </template>
    </div>
  </div>
</template>

<script>
/*
import _ from 'lodash'
*/
import axios from 'axios'

import ICountUp from 'vue-countup-v2'
export default {
  name: 'search',
  props: ['query'],
  mounted: function () {
    let dotInc = setInterval(() => {
      this.dot_ticker++
      switch (this.dot_ticker % 3) {
        case 0:
          this.dots = '.'
          break
        case 1:
          this.dots = '..'
          break
        case 2:
          this.dots = '...'
          break
        default:
          this.dots = '.'
          break
      }
    }, 1000)
    this.$nextTick(function () {
      console.log('requesting ' + this.query)
      axios.get('http://localhost:5000/api/download/' + this.query)
      .then(response => {
        console.log('got ' + this.query)
        clearInterval(dotInc)
        this.download_complete = true
        this.num_images = response.data.num_images
        this.tmp_dir = response.data.dirname
      })
      .catch(() => {
        clearInterval(dotInc)
        this.errored = true
      })
    })
  },
  components: { ICountUp },
  data () {
    return {
      num_images: 0,
      tmp_dir: '',
      dot_ticker: 0,
      dots: '.',
      errored: false,
      download_complete: false
    }
  },
  methods: {
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.request {
  display: flex;
  justify-content: space-around;
}

#cloud-img-wrapper {
 height: 350px;
 width: 503px;
 padding-top: 350px;
 position: relative;
}

#cloud-img {
  height: 300px;
}

h3 {
  position: absolute;
  top: 545px;
  text-align: center;
  left: 0;
  margin: 0 auto;
  width: 100%;
}
.dots {
  width: 32px;
  text-align: left;
  display: inline-block;
}
.bold-italics {
  font-style: italic;
}
</style>
