package com.example.abaland.android_remote;

import android.view.ViewGroup;
import android.widget.TextView;

import java.util.HashMap;


class GeneralFunctions {

    /**
     * Creates or fetches textView corresponding to a worker id.
     *
     * @param activity Activity where textView should be created
     * @param workerViews Hashmap containing all views previously created
     * @param workerId id of worker that just sent response
     * @return previously created view for that worker, or a new view that corresponds to the worker
     */
    static TextView getWorkerView(MainActivity activity, HashMap<String, TextView> workerViews,
                                  String workerId) {

        TextView responseView;
        if (!workerViews.containsKey(workerId)) {

            responseView = new TextView(activity);
            responseView.setLayoutParams(new ViewGroup.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
            workerViews.put(workerId, responseView);

        } else {

            responseView = workerViews.get(workerId);

        }

        return responseView;

    }

}
