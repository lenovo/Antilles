<style >
.antilles-date-picke-date, .antilles-date-picke-label {
  margin-right: 20px;
}
.datePicklabel{
  display: inline-block;
  margin-right: 20px;
  height: 36px;
  line-height: 36px;
}
.datePicklabel a{
  cursor: pointer;
  color: #A0A0A0;
}
.highLight {
  color: #40aaff!important;
}
</style>

<template lang="html">
<div id="tid_date-picker" class="antilles-date-picke-date">
    <el-date-picker id="tid_date-picker-start-time"
      :editable='false'
      name="antilles-date-picker-start-time"
      v-model="startTime"
      align="right"
      type="date"
      :placeholder="$t('Date.Picker.startTime')"
      :picker-options="startPickerOptions">
    </el-date-picker>
    <i style="margin-right:5px;">-</i>
    <el-date-picker id="tid_date-picker-end-time"
      :editable='false'
      v-model="endTime"
      align="right"
      type="date"
      :placeholder="$t('Date.Picker.endTime')"
      :picker-options="endPickerOptions">
    </el-date-picker>
  <div style="display: inline-block; margin-left: 20px;" v-if="quickPickenabel">
    <span class="datePicklabel" v-for="(label, index) in pickerLabelDefault" :key="index">
      <a class="antilles-date-picke-label-style" :class="{highLight: index==currentIndex}" @click="onSetTime(label, index)">{{$t('Date.Picker.' + label.unit, {'size':label.size})}}</a>
    </span>
  </div>
</div>
</template>

<script>
  import Format from './../common/format'
  export default {
  data () {
    return {
      startPickerOptions: this.pickerDateDisabled (this.value[1], 'start'),
      endPickerOptions: this.pickerDateDisabled (this.value[0], 'end'),
      startTime: this.value[0],
      endTime: this.value[1],
      pickerLabelList:['d','day','w','week','m','month'],
      quickPickenabel: this.quickPick &&
                        this.quickPick != "" &&
                        this.quickPick != [] ,
      pickerLabelDefault:[],
      debug: true,
      currentIndex: null,
      optionTime: []
    }
  },
  props: [
    'value',
    'quickPick',
  ],
  mounted () {
    if(this.quickPick) {
      var quickPick = this.quickPick;
      if(quickPick == 'default') {
        quickPick = ['1d', '7d', '30d']
      }
      if(typeof(quickPick) == 'object') {
        this.initPickerLabel(quickPick);
      }
    }

    this.$watch(() => {
      return {
        start: this.startTime,
        end: this.endTime
      }
    }, (newVal, oldVal) => {
      newVal.start=newVal.start?newVal.start:'';
      newVal.end=newVal.end?newVal.end:'';
      this.endPickerOptions = this.pickerDateDisabled (newVal.start, 'end');
      this.startPickerOptions = this.pickerDateDisabled (newVal.end, 'start');

      var start = newVal.start?new Date(Format.formatDateTime(newVal.start, 'yyyy/MM/dd')+' 00:00:00'):'';
      var end = newVal.end?new Date(Format.formatDateTime(newVal.end, 'yyyy/MM/dd')+' 23:59:59'):'';

      var interval = newVal.end - newVal.start

      this.currentIndex = null
      for (var i = 0; i < this.optionTime.length; i++) {
        if (interval == this.optionTime[i]) {
          this.currentIndex = i
        }
      }

      this.$emit('date-change', [start, end]);
    })
  },
  methods: {
    initPickerLabel (quickPick) {
      var optionTime = []
      for (var i = 0; i < quickPick.length; i++) {
        var num = parseInt(quickPick[i])
        var unit = quickPick[i].replace(num, '')
        if (unit == 'd' || unit == 'day') {
          var time = (num - 1) * 3600 * 24 * 1000
        } else if (unit == 'w' || unit == 'week') {
          var time = ((num * 7 ) - 1) * 3600 * 24 * 1000
        } else if (unit == 'm' || unit == 'month') {
          var time = ((num * 31 ) - 1) * 3600 * 24 * 1000
        }
        optionTime.push(time)
      }
      this.optionTime = optionTime;
      quickPick.forEach((item) => {
        var num = parseInt(item);
        var str = item.substr(String(num).length,)
        if (this.pickerLabelList.indexOf(str) !== -1) {
          if(str.length>1){
            str = str.substr(0, 1);
          }
          this.pickerLabelDefault.push({
            size: num,
            unit: num<=1?str:str+'s'
          })
        }
      })
    },
    onSetTime (label, index) {
      this.currentIndex = index
      var num = label.size;
      var str = label.unit
      const oneDayTime = 3600 * 1000 * 24
      const startTime = new Date();
      const endTime = new Date();
      if(str == "d"|| str == 'ds') {
        if(num > 1) {
          startTime.setTime(Date.now() - oneDayTime * (num - 1));
          endTime.setTime(Date.now());
        } else {
          startTime.setTime(Date.now());
          endTime.setTime(Date.now());
        }

      } else if ( str == "w" || str == "ws") {
        startTime.setTime(startTime.getTime() - oneDayTime * 7 * num + 8.64e7);
        endTime.setTime(Date.now());
      } else if ( str == "m" || str == "ms" ) {
        startTime.setTime(startTime.getTime() - oneDayTime * 30 * num);
        endTime.setTime(Date.now());
      }

      this.startTime = startTime;
      this.endTime =  endTime;
    },
    pickerDateDisabled (date, type) {
      return {
        disabledDate (time) {
          if(date){
            if (type == 'start') {
              if(new Date(date) < time.getTime()) {
                return time.getTime() > new Date(date)
              } else {
                return time.getTime() >  Date.now();
              }
            } else {
              return time.getTime() < new Date(date);
            }
          }else {
            return time.getTime() >  Date.now();
          }
        }
      }
    },
    clear () {
      this.currentIndex = null
      this.startTime = '';
      this.endTime = '';
    }


  }

}
</script>
