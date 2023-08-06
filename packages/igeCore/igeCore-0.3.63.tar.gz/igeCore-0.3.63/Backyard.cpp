#include "pyxie.h"
#include "Backyard.h"
#include "pyxieShowcase.h"
#include "pyxieFigure.h"
#include "pyxieCamera.h"
#include "pyxieRenderContext.h"
#include "pyxieRenderTarget.h"
#include "pyxieTime.h"
#include "pyxieProfiler.h"

#include <map>
#include <queue>
#include <mutex>
#include <thread>
#include <vector>
#include <iostream>
#include <exception>
#include <Python.h>

#include "pythonResource.h"
#include "numpy/ndarrayobject.h"

namespace pyxie {

	std::vector<texture_obj*> imageUpdateList;
	void Backyard::UpdateImageRequest(void* tex) {
		if (((texture_obj*)tex)->subImage) {
			Py_INCREF(((texture_obj*)tex)->subImage);
		}
		Py_INCREF((texture_obj*)tex);
		imageUpdateList.push_back((texture_obj*)tex);
	}

	struct RenderSet {
		pyxieCamera* camera;
		pyxieShowcase* showcas;
		pyxieRenderTarget* offscreen;
		bool clearColor;
		bool colearDepth;
		Vec4 color;
	};
	std::vector<RenderSet> renderSets;

	Backyard* Backyard::instance;
	Backyard& Backyard::Instance() { return *instance; }


	std::mutex main_mtx;
	std::mutex python_mtx;

	std::condition_variable main_cv;
	std::condition_variable python_cv;

	bool wake_Main = false;

	bool quitPython = false;
	bool quitRequest = false;

	Backyard::~Backyard() {
		quitRequest = true;
		while (quitPython) {
			python_cv.notify_one();
		}

		for (auto itr = renderSets.begin(); itr != renderSets.end(); ++itr) {
			(*itr).camera->DecReference();
			(*itr).showcas->DecReference();
		}
		renderSets.clear();
	}

	void Backyard::Delete() {
		PYXIE_SAFE_DELETE(instance); 
	}

/*
	std::mutex python_mtx;
	std::condition_variable python_cv;
	bool is_readyPython = false;
	bool wake_Python = true;

	void Backyard::SyncPython() {
		std::unique_lock<std::mutex> python_lk(python_mtx);
		is_readyPython = false;
		wake_Python = false;
		python_cv.wait(python_lk, [] {return is_readyPython; });
		wake_Python = true;
	}
	void Backyard::SyncMain() {
		if (!wake_Python) {
			Render();
			is_readyPython = true;
			python_cv.notify_one();
		}
	}
	void Backyard::WakeBoth() {
		is_readyPython = true;
		python_cv.notify_one();
	}
*/

	void Backyard::WakeBoth() {
		python_cv.notify_one();
		main_cv.notify_one();
	}

	bool Swapframe = true;
	void Backyard::SyncMain() {
		PyxieZoneScoped;
		do{
			//std::this_thread::sleep_for(std::chrono::microseconds(10));

			std::unique_lock<std::mutex> main_lk(main_mtx);

			while(wake_Main)
				python_cv.notify_one();

			main_cv.wait(main_lk);
			wake_Main = true;
			Render();
		}while (!Swapframe);
	}

	void Backyard::SyncPython(bool swapframe) {
		//std::this_thread::sleep_for(std::chrono::microseconds(10));
		PyxieZoneScoped;
		std::unique_lock<std::mutex> python_lk(python_mtx);

		Swapframe = swapframe;

		while (!wake_Main)
			main_cv.notify_one();
		python_cv.wait(python_lk);
		wake_Main = false;		

		if (Swapframe)
		{
			PyxieFrameMark;
		}
		if (quitRequest) {
			quitPython = true;
			PyRun_SimpleString("import os\nos._exit(0)");
		}

	}


	void Backyard::RenderRequest(pyxieCamera* camera, pyxieShowcase* showcase, pyxieRenderTarget* offscreen, bool clearColor, bool clearDepth, const float* color){
		camera->IncReference();
		showcase->IncReference();

		RenderSet rset;
		rset.camera = camera;
		rset.showcas = showcase;
		rset.offscreen = offscreen;
		rset.clearColor = clearColor;
		rset.colearDepth = clearDepth;
		rset.color = Vec4(color[0], color[1], color[2], color[3]);
		renderSets.push_back(rset);
		SyncPython(false);
	}

	void Backyard::Render() {
		PyxieZoneScoped;
		for (auto itr = imageUpdateList.begin(); itr != imageUpdateList.end(); ++itr) {
			if ((*itr)->subImage) {
				uint8_t* bmp = NULL;
				int w, h, x, y;
				if (PyBytes_Check((*itr)->subImage)) {
					bmp = (uint8_t*)PyBytes_AsString((*itr)->subImage);
					x = (*itr)->x;
					y = (*itr)->y;
					w = (*itr)->w;
					h = (*itr)->h;
				}
				else if ((*itr)->subImage->ob_type->tp_name && strcmp((*itr)->subImage->ob_type->tp_name, "numpy.ndarray") == 0) {
					PyArrayObject_fields* ndarray = (PyArrayObject_fields*)(*itr)->subImage;
					bmp = (uint8_t*)ndarray->data;
					x = (*itr)->x;
					y = (*itr)->y;
					h = *ndarray->dimensions;
					w = *ndarray->strides / ndarray->nd;
				}
				if(bmp) (*itr)->colortexture->UpdateSubImage(bmp, x, y, w, h);
				Py_DECREF((*itr)->subImage);
				Py_DECREF(*itr);
			}
		}
		imageUpdateList.clear();

		pyxieRenderContext& renderContext = pyxieRenderContext::Instance();

		for (auto itr = renderSets.begin(); itr != renderSets.end(); ++itr) {
			{
				PyxieZoneScopedN("BeginScene");
				renderContext.BeginScene((*itr).offscreen, (*itr).color, (*itr).clearColor, (*itr).colearDepth);
			}			
			{
				PyxieZoneScopedN("showcas Update");
				(*itr).showcas->Update(0.0f);
			}
			{
				PyxieZoneScopedN("camera Render");
				(*itr).camera->Render();
			}
			{
				PyxieZoneScopedN("showcas Render");
				(*itr).showcas->Render();
			}
			
			{
				PyxieZoneScopedN("EndScene");
				renderContext.EndScene();
			}
			
			(*itr).camera->DecReference();
			(*itr).showcas->DecReference();
		}
		renderSets.clear();
	}

	static bool finishFlag = false;
	void Backyard::SetFinishProgram(bool finish) {
		finishFlag = finish;
	}
	bool Backyard::IsProgramRunning() {
		return !finishFlag;
	}


}
