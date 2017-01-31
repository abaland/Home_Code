package com.example.abaland.android_remote;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;

import android.view.Menu;
import android.view.MenuItem;
import android.view.View;

import android.widget.*;
import java.util.Locale;


public class AirconActivity extends AppCompatActivity {

    private Toolbar toolbar;

    private Switch airconStateSwitch;
    private RadioGroup airconModeRadio;
    private SeekBar airconTemperature;
    private TextView airconTemperatureText;
    private Spinner fanSpeedSpinner;
    private Spinner fanDirectionSpinner;

    // Defaults
    private boolean airconState = true;
    private String airconMode = "heat";
    private Integer airconTemp = 24;
    private String fanSpeed = "auto";
    private String fanDirection = "auto";



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.aircon_remote);

        toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        ////////////////
        // Start added.
        ////////////////

        // Links all GUI items to the script
        airconStateSwitch = (Switch) findViewById(R.id.Aircon_Power);
        airconModeRadio = (RadioGroup) findViewById(R.id.Aircon_Mode);
        airconTemperature = (SeekBar) findViewById(R.id.Aircon_Temperature);
        airconTemperatureText = (TextView) findViewById(R.id.Aircon_Temperature_Text);
        fanSpeedSpinner = (Spinner) findViewById(R.id.Aircon_Speed);
        fanDirectionSpinner = (Spinner) findViewById(R.id.Aircon_Direction);

        // Updates GUI correctly based on defaults
        airconStateSwitch.setChecked(airconState);

        switch (airconMode) {
            case  "heat":
                findViewById(R.id.Aircon_Heater).setSelected(true);
                break;
            case "dry":
                findViewById(R.id.Aircon_Dry).setSelected(true);
                break;
            case "cool":
                findViewById(R.id.Aircon_Cooler).setSelected(true);
                break;
        }

        // Converts from [16, 31] range to [0, 15]
        airconTemperature.setProgress(airconTemp - 16);
        airconTemperatureText.setText(String.format(Locale.US, "%d", airconTemp - 16));



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


    /**
     * Applies appropriate function when button on GUI is clicked.
     *
     * Uses text on button and mapping created to get more information about what should be sent.
     *
     * @param v Button clicked, as a View object.
     */
    void onClickFunction(View v){

        String RemoteName = "aircon";

        // Casts button clicked as a Button instance, and gets its text content.
        Button clickedButton = (Button) v;
        String ButtonText = clickedButton.getText().toString();

        System.out.println(ButtonText);

        Rabbit_Manager rabbit_manager = new Rabbit_Manager();
        rabbit_manager.publishMessage(RemoteName, KeyToPress);

    }

}
