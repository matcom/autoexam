class AddStuffToClavePregunta < ActiveRecord::Migration
  def change
    add_column :clave_pregunta, :minimo, :integer
    add_column :clave_pregunta, :maximo, :integer
  end
end
