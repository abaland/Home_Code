package com.example.abaland.android_remote;

import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.HashMap;

import org.w3c.dom.Document;


class TemperatureControls {

    private MainActivity activity;

    private Button querryButton;
    private LinearLayout querryResults;
    private HashMap<String, TextView> workerViews = new HashMap<>();

    private RabbitCallback callbackObject;


    TemperatureControls(MainActivity activity) {

        this.activity = activity;

    }


    /**
     * Applies appropriate function when button on GUI is clicked.
     */
    private void onClickFunction(){

        MainActivity activity = TemperatureControls.this.activity;

        String messageToSend = "<instruction type=\"sensors\" target=\"bedroom,living\"/>";

        activity.rabbitManager.askWorker("sensors", messageToSend, activity,
                callbackObject, 5000);

    }


    /**
     */
    private void setUpCallbackFunction() {

        callbackObject = new RabbitCallback() {

            @Override
            public void execute(final Document messageToProcess) {

                // Starts an UI-interactive thread to update the view with the received message.
                activity.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {

                        String workerId = messageToProcess.getDocumentElement().getAttribute("id");

                        TextView responseView = GeneralFunctions.getWorkerView(activity,
                                workerViews, workerId);

/*                        int totalChildren = messageToProcess.getDocumentElement().children.size();
                          for (int sensorIndex=0 ; sensorIndex<totalChildren ; sensorIndex++) {
                            int totalMeasures = messageToProcess.getDocumentElement().children[sensorIndex].attributes.size();
                            for (int measureIndex=0 ; measureIndex<totalMeasures ; measureIndex++) {


                                System.out.println();

                            }

                        }
*/
                        responseView.setText(workerId);
                        querryResults.addView(responseView);

                    }

                });

            }

        };

    }


    /**
     * Binds all elements from GUI (spinner, buttons, ...) to the script internal parameters
     */
    private void bindGUIToScript() {

        querryButton = (Button) this.activity.findViewById(R.id.temperature_querry);

        querryResults = (LinearLayout) this.activity.findViewById(R.id.temperature_layout);

    }


    /**
     * Adds all listeners to GUI elements, to update internal parameters, send commands, ...
     */
    private void addGUIListeners() {

        querryButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){onClickFunction();}

        });

    }


    void initialize() {

        setUpCallbackFunction();

        // Links all GUI items to the script
        bindGUIToScript();

        // Adds listeners to GUI, to update internal parameters/take appropriate actions on change
        addGUIListeners();

    }

}
