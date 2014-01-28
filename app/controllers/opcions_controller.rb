class OpcionsController < ApplicationController
  before_action :set_opcion, only: [:show, :edit, :update, :destroy]

  # GET /opcions
  # GET /opcions.json
  def index
    @opcions = Opcion.all
  end

  # GET /opcions/1
  # GET /opcions/1.json
  def show
  end

  # GET /opcions/new
  def new
    @opcion = Opcion.new
  end

  # GET /opcions/1/edit
  def edit
  end

  # POST /opcions
  # POST /opcions.json
  def create
    @opcion = Opcion.new(opcion_params)

    respond_to do |format|
      if @opcion.save
        format.html { redirect_to @opcion, notice: 'Opcion was successfully created.' }
        format.json { render action: 'show', status: :created, location: @opcion }
      else
        format.html { render action: 'new' }
        format.json { render json: @opcion.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /opcions/1
  # PATCH/PUT /opcions/1.json
  def update
    respond_to do |format|
      if @opcion.update(opcion_params)
        format.html { redirect_to @opcion, notice: 'Opcion was successfully updated.' }
        format.json { head :no_content }
      else
        format.html { render action: 'edit' }
        format.json { render json: @opcion.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /opcions/1
  # DELETE /opcions/1.json
  def destroy
    @opcion.destroy
    respond_to do |format|
      format.html { redirect_to opcions_url }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_opcion
      @opcion = Opcion.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def opcion_params
      params.require(:opcion).permit(:preguntum_id, :titulo, :right)
    end
end
