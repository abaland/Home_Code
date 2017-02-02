package com.example.abaland.android_remote;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;

import android.view.Menu;
import android.view.MenuItem;
import android.view.View;

import android.widget.*;

import java.util.HashMap;
import java.util.Locale;

import android.util.Log;


public class AirconActivity extends AppCompatActivity {

    // GUI Objects
    private Switch airconStateSwitch;
    private RadioGroup airconModeRadio;
    private SeekBar airconTemperatureSeekBar;
    private TextView airconTemperatureText;
    private Spinner fanSpeedSpinner;
    private Spinner fanDirectionSpinner;
    private Button sendButton;

    // Defaults values/indexes
    private boolean airconState = true;
    private Integer airconModeIndex = 0; // 0: heat, 1: dry, 2: cold.
    private Integer airconTemperature = 24;
    private Integer fanSpeedIndex = 0; // 0:auto, 1: weak, 2: middle, 3: strong
    private Integer fanDirectionIndex = 0; //0:auto, 1: loop, 2: lowest, 3: low, 4: middle, 5: high, 6: highest

    // Mapping from index to value.
    private HashMap<Boolean, String> airconStateMapping = new HashMap<>();
    private String[] airconModeMapping = {"heat", "dry", "cool"};
    private String[] fanSpeedMapping = {"auto", "weak", "middle", "strong"};
    private String[] fanDirectionMapping = {"auto", "loop", "lowest", "low", "middle", "high", "highest"};


    /**
     * Querries all elements from aircon GUI to get related configuration as a string.
     *
     * @return Comma-separated aircon configuration, following syntax of "on,heat,25,strong,loop"
     */
    private String getConfigAsString(){

        String fullConfig = "";

        // Updates GUI correctly based on defaults
        fullConfig += airconStateMapping.get(airconState) + ",";
        fullConfig += airconModeMapping[airconModeIndex] + ",";
        fullConfig += String.valueOf(airconTemperature) + ",";
        fullConfig += fanSpeedMapping[fanSpeedIndex] + ",";
        fullConfig += fanDirectionMapping[fanDirectionIndex];

        ///////////////////
        return fullConfig;
        ///////////////////

    }


    /**
     * Binds all elements from GUI (spinner, buttons, ...) to the script internal parameters
     */
    private void bindGUIToScript() {

        airconStateSwitch = (Switch) findViewById(R.id.Aircon_Power);
        airconModeRadio = (RadioGroup) findViewById(R.id.Aircon_Mode);
        airconTemperatureSeekBar = (SeekBar) findViewById(R.id.Aircon_Temperature);
        airconTemperatureText = (TextView) findViewById(R.id.Aircon_Temperature_Text);
        fanSpeedSpinner = (Spinner) findViewById(R.id.Aircon_Speed);
        fanDirectionSpinner = (Spinner) findViewById(R.id.Aircon_Direction);
        sendButton = (Button) findViewById(R.id.Send_Aircon_Signal);

    }


    /**
     * Initializes values from GUI elements. Uses default value defined above.
     *
     * TODO : add User preferences to default
     */
    private void initializeGUIValues() {

        // Turns On/Off switch
        airconStateSwitch.setChecked(airconState);

        // Checks correct aircon mode
        switch (airconModeIndex) {

            case  0:

                findViewById(R.id.Aircon_Heater).setSelected(true);
                break;

            case 1:

                findViewById(R.id.Aircon_Dry).setSelected(true);
                break;

            case 2:

                findViewById(R.id.Aircon_Cooler).setSelected(true);
                break;

        }

        // Sets progress bar for temperature (and related text). Converts from real [16, 31] range to GUI [0, 15].
        airconTemperatureSeekBar.setProgress(airconTemperature - 16);
        airconTemperatureText.setText(String.format(Locale.US, "%d", airconTemperature - 16));

        // Assigns both spinners for fan speed/direction.
        fanSpeedSpinner.setSelection(fanSpeedIndex);
        fanDirectionSpinner.setSelection(fanDirectionIndex);

    }


    /**
     * Adds all listeners to GUI elements, to update internal parameters, send commands, ...
     */
    private void addGUIListeners() {

        // Adds listener to On/Off state switch (updates airconState)
        airconStateSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {

            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {

                // Updates internal parameter
                airconState = isChecked;
                Log.v("Aircon", getConfigAsString());

            }

        });


        // Adds listener for aircon mode radio buttons.
        airconModeRadio.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {

            @Override
            public void onCheckedChanged (RadioGroup group,int checkedId){

                // Updates internal parameter
                airconModeIndex = checkedId;
                Log.v("Aircon", getConfigAsString());

            }

        });


        // Adds listener for aircon temperature seekbar
        airconTemperatureSeekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {

                // Updates internal parameter
                airconTemperature = progress + 16;
                Log.v("Aircon", getConfigAsString());

                // Updates text GUI element with current temperature
                airconTemperatureText.setText(String.valueOf(airconTemperature));

            }

        });


        // Adds listener for the fan speed spinner
        fanSpeedSpinner.setOnItemSelectedListener(new Spinner.OnItemSelectedListener() {

            @Override
            public void onItemSelected(AdapterView<?> parentView, View selectedItemView, int position, long id) {

                // Updates internal parameter
                fanSpeedIndex = position;
                Log.v("Aircon", getConfigAsString());
            }

            @Override
            public void onNothingSelected(AdapterView<?> parentView) {}

        });


        // Adds listener for the fan direction spinner
        fanDirectionSpinner.setOnItemSelectedListener(new Spinner.OnItemSelectedListener() {

            @Override
            public void onItemSelected(AdapterView<?> parentView, View selectedItemView, int position, long id) {

                // Updates internal parameter
                fanDirectionIndex = position;
                Log.v("Aircon", getConfigAsString());
            }

            @Override
            public void onNothingSelected(AdapterView<?> parentView) {}

        });


        // Adds listener for configuration send button
        sendButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){

                String RemoteName = "aircon";
                Log.v("Aircon", getConfigAsString());

                // Casts button clicked as a Button instance, and gets its text content.
                Rabbit_Manager rabbit_manager = new Rabbit_Manager();
                rabbit_manager.publishMessage(RemoteName, getConfigAsString());

            }

        });
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.aircon_remote);


        setSupportActionBar((Toolbar) findViewById(R.id.toolbar));

        ////////////////
        // Start added.
        ////////////////
        Log.v("Aircon", getConfigAsString());

        // Initializes the mapping of index-to-value for the only hashmap existing
        airconStateMapping.put(false, "off");
        airconStateMapping.put(true, "on");

        // Links all GUI items to the script
        bindGUIToScript();

        // Updates GUI correctly based on defaults
        initializeGUIValues();

        // Adds all listeners to GUI elements, to update internal parameters / take appropriate actions on change
        addGUIListeners();

    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {

        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;

    }


    @Override
    public boolean onOptionsItemSelected(MenuItem item) {

        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {

            return true;

        }

        return super.onOptionsItemSelected(item);

    }

}
