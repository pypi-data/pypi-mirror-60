// Copyright (c) Nicolas Fernandez.
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel, DOMWidgetView, ISerializers
} from '@jupyter-widgets/base';

import {
  MODULE_NAME, MODULE_VERSION
} from './version';

import cgm_fun from 'clustergrammer-gl';

import * as d3 from 'd3';

console.log('********************************************')
console.log('** clustergrammer2 frontend version 0.5.12 **')
console.log('********************************************')
console.log('working on traitlets for Voila')

export
class ExampleModel extends DOMWidgetModel {
  defaults() {
    return {...super.defaults(),
      _model_name: ExampleModel.model_name,
      _model_module: ExampleModel.model_module,
      _model_module_version: ExampleModel.model_module_version,
      _view_name: ExampleModel.view_name,
      _view_module: ExampleModel.view_module,
      _view_module_version: ExampleModel.view_module_version,
      value : 'javascript set value!!!',
      network: ''
    };
  }

  static serializers: ISerializers = {
      ...DOMWidgetModel.serializers,
      // Add any extra serializers here
    }

  static model_name = 'ExampleModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'ExampleView';   // Set to null if no view
  static view_module = MODULE_NAME;   // Set to null if no view
  static view_module_version = MODULE_VERSION;
}

function make_viz(args, cgm_model){
  args.container = document.getElementById(args.container_name);
  cgm_fun(args, cgm_model);

  // // exposing all of cgm, eventually want to only expose a few methods
  // // cgm_model.cgm = cgm;
  // cgm_model.destroy_viz = cgm.destroy_viz;

}

var my_widget_callback = function(external_model){

  // console.log('my_widget_callback')

  var cgm = external_model.cgm;
  var params = cgm.params;
  var inst_value;

  // switch(params.tooltip.tooltip_type) {
  //   case 'row-label':

  //     // update row/column
  //     ////////////////////////
  //     inst_value = params.tooltip.tooltip_type + ' -> ' + String(params.int.mouseover.row.name)
  //     external_model.model.set('value', inst_value);
  //     external_model.touch();

  //     break;

  //   case 'col-cat-0':

  //     // update category
  //     ////////////////////////
  //     // params.int.mouseover[inst_axis].cats[mouseover_cat_index]
  //     inst_value = params.tooltip.tooltip_type + ' -> ' + String(params.int.mouseover['col'].cats[0])
  //     external_model.model.set('value', inst_value);
  //     external_model.touch();

  //     break;

  //   case 'col-dendro':

  //     inst_value = params.tooltip.tooltip_type + ' -> ' + String(params.dendro.selected_clust_names)
  //     external_model.model.set('value', inst_value);
  //     external_model.touch();

  //     break;

  //   default:

  //     inst_value = params.tooltip.tooltip_type + ' -> ' // 'other'

  //     // update other
  //     ////////////////////////
  //     // external_model.model.set('value', String(null));
  //     external_model.model.set('value', inst_value);
  //     external_model.touch();

  //     break;
  // }

  if (params.tooltip.tooltip_type === 'row-label'){

    // update row/column
    ////////////////////////
    inst_value = params.tooltip.tooltip_type + ' -> ' + String(params.int.mouseover.row.name)
    external_model.model.set('value', inst_value);
    external_model.touch();

  } else if (params.tooltip.tooltip_type === 'col-cat-0'){

    // update category
    ////////////////////////
    // params.int.mouseover[inst_axis].cats[mouseover_cat_index]
    inst_value = params.tooltip.tooltip_type + ' -> ' + String(params.int.mouseover['col'].cats[0])
    external_model.model.set('value', inst_value);
    external_model.touch();

  } else {

    inst_value = params.tooltip.tooltip_type // 'other'

    // update other
    ////////////////////////
    // external_model.model.set('value', String(null));
    external_model.model.set('value', inst_value);
    external_model.touch();

  }

}

export
class ExampleView extends DOMWidgetView {
  render() {

    d3.select(this.el)
      .append('div')
      .attr('id', this.cid)
      .style('width', '900px')
      .style('height', '1035px')
      .style('border', '2px solid #eee');

    // define arguments object
    var args = {
        'container_name': this.cid,
        'network': JSON.parse(this.model.get('network')),
        'viz_width' : 900,
        'viz_height': 900,
        // 'widget_model': this,
        'widget_callback': my_widget_callback
    };

    setTimeout(make_viz, 10, args, this);

    this.model.on('change:value', this.value_changed, this);


  }

  value_changed() {

    // this can be used to update cgm on a value change to the widget_model
    // e.g. reorder cgm based on value change to widget traitlet

    // console.log('widget_model.value_changed')
    // console.log('--------------------------')
    // console.log(this)
    // this.el.textContent = this.model.get('value');
    // console.log('value', this.model.get('value'));

    // // see https://stackoverflow.com/questions/55834241/ts2339-property-name-does-not-exist-on-type-object
    // console.log(this['cgm'])
    // this['cgm'].destroy_viz()

    // this['destroy_viz']();

  }

}



