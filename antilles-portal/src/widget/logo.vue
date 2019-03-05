<style lang="css">
.main-logo {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 60px;
  background-color: #3A4556;
}
.logo-max {
  background: url('./../asset/image/main/logo-max.png') no-repeat;
  height: 35px;
  width: 50%;
  display: inline-block;
}
.logo-min {
  background: url('./../asset/image/main/logo-min.png') no-repeat;
  height: 35px;
  display: inline-block;
   width: 50%;
}
</style>
<template lang="html">
<div class="main-logo">
  <a :href="logolink" :class="isMinLogo?logoMin:logoMax"></a>
</div>
</template>

<script>

export default {
  data () {
    return {
      logolink: "",
      logoMax: "logo-max",
      logoMin: "logo-min",
      isMinLogo: gApp.isCollapse,

    }
  },
  props: [
    'logoUrl'
  ],
  mounted () {
    this.logolink = '#' + this.logoUrl;
    var _this = this;
    gApp.$watch('isCollapse',function (newValue, oldValue) {
      _this.isMinLogo = newValue
    })
  },
  watch: {
    logoUrl(val, oldVal) {
      this.logolink = '#' + val;
    }
  },
  methods: {
    
  }
}
</script>
