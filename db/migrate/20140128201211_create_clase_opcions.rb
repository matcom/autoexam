class CreateClaseOpcions < ActiveRecord::Migration
  def change
    create_table :clase_opcions do |t|
      t.integer :opcion_id
      t.integer :clave_preguntum_id
      t.boolean :correcta
      t.integer :puntos_bien
      t.integer :puntos_mal

      t.timestamps
    end
  end
end
