class CreateClavePregunta < ActiveRecord::Migration
  def change
    create_table :clave_pregunta do |t|
      t.integer :preguntum_id
      t.integer :examan_id
      t.integer :total_puntos
      t.text :nota_especial

      t.timestamps
    end
  end
end
