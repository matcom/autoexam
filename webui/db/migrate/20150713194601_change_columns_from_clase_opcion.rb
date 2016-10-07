class ChangeColumnsFromClaseOpcion < ActiveRecord::Migration
  def change
  	change_column :clase_opcions, :puntos_bien, :decimal
  	change_column :clase_opcions, :puntos_mal, :decimal
  end
end
