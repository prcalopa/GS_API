/*
 ==============================================================================
 
 PyJUCEParameter.cpp
 Created: 6 Jul 2016 10:36:47am
 Author:  martin hermant
 
 ==============================================================================
 */

#include "PyJUCEParameter.h"
#include "PyJUCEAPI.h"

class PyVar : public ReferenceCountedObject{
public :

  PyVar(PyObject * _ref):ref(_ref){
    Py_IncRef(ref);

  }

  ~PyVar(){
    Py_DecRef(ref);
  }
  typedef ReferenceCountedObjectPtr<PyVar> Ptr;
  PyObject * ref;

};

 var pyToVar(PyObject * o){
  var  res = var::undefined();

  if(PyInt_CheckExact(o)){	res = (int)PyInt_AsLong(o);}
  else if(PyFloat_CheckExact(o)){res = (double)PyFloat_AsDouble(o);}
  else if(PyString_CheckExact(o)){res = (char *)PyString_AsString(o);}
  else if (PyBool_Check(o)){res = (bool) (o==Py_True);}
  else if(PyList_CheckExact(o)){
    res = var();
    int size = PyList_GET_SIZE(o);
    for(int i = 0; i <size;i++){
      var elem = pyToVar(PyList_GET_ITEM(o, i));
      res.append(elem);;
    }
  }
  else if(PyDict_CheckExact(o)){
    res = var(new DynamicObject());
    Py_ssize_t pos=0;
    PyObject *key;
    PyObject *value;
    while(PyDict_Next(o, &pos, &key, &value)){
      if(PyString_CheckExact(key)){
        res.getDynamicObject()->setProperty(Identifier(PyString_AsString(key)),pyToVar(value));
      }
      else{
        DBG("dict with non string key not supported");
      }
    }

  }
  else if (o==Py_None){res = var::undefined();}
  else if(PyCallable_Check(o)){
    res = var(new PyVar(o));
  }
  return res;
}

 PyObject * varToPy(var v){
  if(v.isInt()){return PyInt_FromLong((int)v);}
  else if(v.isBool()){return PyBool_FromLong((int)v);}
  else if(v.isDouble()){return PyFloat_FromDouble((double)v);}
  else if(v.isString()){return PyString_FromString(v.toString().toRawUTF8());}
  else if(v.isArray()){
    int size =v.getArray()->size();
    PyObject * res = PyList_New(size);
    for(int i = 0 ; i < size ; i++){
      PyList_SetItem(res, i, varToPy(v.getArray()->getUnchecked(i)));
    }
    return res;
  }
  else if(v.getDynamicObject()){
    DynamicObject * d = v.getDynamicObject();
    int size =d->getProperties().size();
    PyObject * res = _PyDict_NewPresized(size);

    for (int i = 0  ; i  < size ; i++){
      PyObject * key = PyString_FromString(d->getProperties().getName(i).toString().toRawUTF8());
      PyObject * value = varToPy(d->getProperties().getValueAt(i));
      PyDict_SetItem(res, key, value);
    }

    return res;

  }
  else if (v.getObject()){
    PyVar::Ptr p = dynamic_cast<PyVar*>(v.getObject());
    if(p ){return p->ref;}
  }

  Py_RETURN_NONE;

}



void PyJUCEParameter::setValue(var v){
	value=v;
	pyJuceApi->py.callFunction(cbFunc,pyJuceApi->interfaceModule,getPythonObject());;
}

var PyJUCEParameter::getValue(){return value;}

Component * PyJUCEParameter::buildComponent(bool unique ){
	Component * res = createComponent( value,properties);
	if (res) {
		var * x,*y,*w,*h;
    if((x=properties.getVarPointer("x")) &&
				(y=properties.getVarPointer("y")) &&
				(w=properties.getVarPointer("width")) &&
				(h=properties.getVarPointer("height")))
		{
			relativeArea.setBounds(*x, *y, *w, *h);
		}
		else{DBG("no size given");}
	}

  if(unique)
    component = res;
	return res;
	
}

void PyJUCEParameter::linkToJuceApi(PyJUCEAPI * p){pyJuceApi=p;};

void PyJUCEParameter::setPythonCallback(PyObject * cb){
	cbFunc = cb;
}

class PyFloatParameter:public PyJUCEParameter,public SliderListener{
public:
  PyFloatParameter(const String & n):PyJUCEParameter(n){}
  
	
	void sliderValueChanged (Slider* slider) override{setValue(slider->getValue());}
#define ASSIGN_STYLE(x) if(styleName==_toxstr(x)){style = Slider::SliderStyle::x;}

	Component *  createComponent(var v,const NamedValueSet & properties) override{
    Slider::SliderStyle style;

    String styleName = properties.getWithDefault("style", "LinearVertical");
    ASSIGN_STYLE(LinearHorizontal)
    ASSIGN_STYLE(LinearVertical)
    ASSIGN_STYLE(LinearBar)
    ASSIGN_STYLE(LinearBarVertical)
    ASSIGN_STYLE(Rotary)
    ASSIGN_STYLE(RotaryHorizontalDrag)
    ASSIGN_STYLE(RotaryVerticalDrag)
    ASSIGN_STYLE(RotaryHorizontalVerticalDrag)
    ASSIGN_STYLE(IncDecButtons)


		Slider * s = new Slider(style, juce::Slider::TextEntryBoxPosition::TextBoxBelow);
    
    s->setName(name);
    s->setRange(properties.getWithDefault("min",0),properties.getWithDefault("max",1),properties.getWithDefault("step", 0));

		s->addListener(this);
		return s;
	}
	
	PyObject * getPythonObject() override{return PyFloat_FromDouble(value);}
};


class PyBoolParameter:public PyJUCEParameter,ButtonListener{
  public:
  PyBoolParameter(const String & n):PyJUCEParameter(n){}
  void buttonClicked(Button *b)override{setValue(b->getToggleStateValue());}
  Component *  createComponent(var v,const NamedValueSet & properties) override{
    TextButton * tb =  new TextButton(name);
    tb->setClickingTogglesState(true);
    tb->addListener(this);

    return tb;

  }

  PyObject * getPythonObject() override{return PyBool_FromLong(value?1:0);}

};

class PyEventParameter:public PyJUCEParameter,ButtonListener{
    public:
    PyEventParameter(const String & n):PyJUCEParameter(n){}
    void buttonClicked(Button *b)override{setValue(var::undefined());}
    Component *  createComponent(var v,const NamedValueSet & properties) override{
      TextButton * tb =  new TextButton(name);
      tb->setClickingTogglesState(false);
      tb->addListener(this);

      return tb;

    }

    PyObject * getPythonObject() override{return Py_None;}
};

class PyEnumParameter:public PyJUCEParameter,ButtonListener{
public:
  PyEnumParameter(const String & n):PyJUCEParameter(n){

  }
  void buttonClicked(Button *b)override{
    if(!b->getToggleState()) return;
    int index(1);
    var flatArray = var();
    PopupMenu m = buildFromVarList(list,index,flatArray);
    int res = m.showAt(b);

    if(res>0){
      setValue(flatArray.getArray()->getUnchecked(res-1));
    }
    b->setToggleState(false, NotificationType::dontSendNotification);
  }

  PopupMenu buildFromVarList(var varList,int & index,var & flatArray){
    PopupMenu m;

    if(varList.getArray()){
    for (auto & v:*varList.getArray()){
      m.addItem((index ++), v.toString());
      flatArray.append(v);
    }
    }
    else if(varList.getDynamicObject()){
      NamedValueSet nvSet = varList.getDynamicObject()->getProperties();
      int size = nvSet.size();
      for (int i = 0 ; i < size ; i++){
        var elem = nvSet.getValueAt(i);

        if(!elem.getDynamicObject() && !elem.getArray())
          {m.addItem(index++, nvSet.getName(i).toString());
            flatArray.append(nvSet.getValueAt(i));}
        else
          {m.addSubMenu(nvSet.getName(i).toString(), buildFromVarList(nvSet.getValueAt(i),index,flatArray));}
      }
    }
    else{
      m.addItem(index++,varList.toString());
      flatArray.append(varList);
    }
    return m;
  }



  Component *  createComponent(var v,const NamedValueSet & properties) override{
    list = properties.getWithDefault("choicesList", Array<var>());
    if(!list.getArray() && !list.getDynamicObject()){
      list = var();
      list.append("emptyList");
    }
    TextButton * tb =  new TextButton(name);
    tb->setClickingTogglesState(true);
    tb->addListener(this);

    return tb;

  }

  var list;
  PyObject * getPythonObject() override{return varToPy(value);}
};






PyJUCEParameter * PyJUCEParameterBuilder::buildParamFromObject( PyObject* o){
	NamedValueSet properties;
	PyObject* props = PyObject_Dir(o);
	if(props && 		PyList_Check(props)){


    int size = PyList_Size(props);
    for(int i = 0 ; i < size ; i++){
      PyObject *key = PyList_GetItem(props, i);
      PyObject *value = PyObject_GetAttr(o, key);
      if(!PyCallable_Check(value) && !String(PyToString(key)).startsWith("__")){
        DBG("parsing "+String(PyString_AsString(key)));
        var v = pyToVar(value);
        if(!v.isUndefined())properties.set(PyString_AsString(key), v);
        else{DBG("cant find type for param property :" << PyString_AsString(key));}
      }
		}
	}
	
	
	
	
	PyJUCEParameter* res = nullptr;
	PyObject * value = PyObject_GetAttrString(o, "_UIParameter__value");
  String className (o->ob_type->tp_name);
  String paramName = properties.getWithDefault("name", className+"_defaultName");
	if(!value){DBG("ui element not valid");jassertfalse;return nullptr;}
  if ((PyLong_CheckExact(value)|| PyInt_CheckExact(value)) && properties.contains("choicesList")){
    res = new PyEnumParameter(paramName);
  }
	else if( PyLong_CheckExact(value)|| PyInt_CheckExact(value)||PyFloat_CheckExact(value) || PyInt_CheckExact(value))
    {res = new PyFloatParameter(paramName);
      if((PyLong_CheckExact(value) || PyInt_CheckExact(value)) && !properties.contains("step")){properties.set("step", 1);}
    }
	else if(PyBool_Check(value))
    {res = new PyBoolParameter(paramName);}
  else if(value == Py_None)
    {res = new PyEventParameter(paramName);}

	else {
		DBG("ui element not supported : " <<className);
	}
	if(res){
		res->setPythonCallback(PyObject_GetAttrString(o, "setValue"));
		res->properties = properties;
	}
	return res;
}