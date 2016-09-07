/*
  ==============================================================================

    pythonWrap.h
    Created: 9 Jun 2016 10:52:18am
    Author:  Martin Hermant

  ==============================================================================
*/

#ifndef PYTHONWRAP_H_INCLUDED
#define PYTHONWRAP_H_INCLUDED

#include "PythonUtils.h"


#include <string>
#include <iostream>
using namespace std;


class PythonWrap{
    public :

    PythonWrap(){}
	~PythonWrap(){deinit();}
    string test(const string& s,PyObject * module);
  
    void printPyState();
  void init( string root="", string  bin="");
	void setFolderPath(const string & s);
    PyObject* loadModule(const string & name,PyObject * oldModule=nullptr);
    void initSearchPath();
    void addSearchPath(const string &);
    
	PyObject * callFunction(const string & func,PyObject * module,PyObject * args=nullptr);
	PyObject * callFunction(PyObject * func,PyObject * module,PyObject * args);
		void deinit();
    
private:
    void prependEnvPath(const string &env,const string& newpath);
    void printEnv(const string & p);
	string curentFolderPath;
  string rootPath;



};




#endif  // PYTHONWRAP_H_INCLUDED
